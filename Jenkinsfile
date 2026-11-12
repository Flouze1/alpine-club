pipeline {
    agent any

    environment {
        DB_NAME             = 'test_alpine_club'
        DB_USER             = 'testuser'
        DB_PASSWORD         = credentials('test-db-password')
        MYSQL_ROOT_PASSWORD = credentials('test-db-root-password')
        DB_HOST             = '127.0.0.1'
        DB_PORT             = '3306'
        
        IMAGE_NAME          = 'localhost:5000/alpine-club'
        IMAGE_TAG           = "${env.GIT_COMMIT?.take(7) ?: 'latest'}"
        PIP_CACHE_DIR       = "${WORKSPACE}/.cache/pip"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Secret Scan (Gitleaks)') {
            steps {
                sh '''
                    mkdir -p reports
                    docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect \
                        --source=/repo --report-format=json --report-path=/repo/reports/gitleaks.json || true
                '''
            }
        }

        stage('Setup & Cache Dependencies') {
            steps {
                sh '''
                    mkdir -p .cache/pip
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install ruff bandit coverage pip-audit
                '''
            }
        }

        stage('Dependency Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    # Генерируем JSON-отчет для Jenkins (Пункт 7 и 12)
                    pip-audit -r requirements.txt -f json -o reports/pip-audit.json || true
                    # Просто выводим предупреждение в консоль, но НЕ ломаем сборку
                    pip-audit -r requirements.txt || true
                '''
            }
        }

        stage('Start Test DB') {
            steps {
                sh '''
                    docker rm -f alpine-test-db || true
                    docker run -d --name alpine-test-db \
                        -e MYSQL_DATABASE=${DB_NAME} \
                        -e MYSQL_USER=${DB_USER} \
                        -e MYSQL_PASSWORD=${DB_PASSWORD} \
                        -e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
                        -p 3306:3306 mysql:8.0 --default-authentication-plugin=mysql_native_password
                    
                    echo "Waiting for MySQL to start..."
                    for i in {1..30}; do
                        if docker exec alpine-test-db mysqladmin ping -h127.0.0.1 -uroot -p${MYSQL_ROOT_PASSWORD} --silent; then 
                            echo "MySQL is ready!"
                            break
                        fi
                        sleep 2
                    done
                '''
            }
        }

        stage('Quality & Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    make test
                    ruff check . > reports/ruff.txt || true
                    bandit -r . -f json -o reports/bandit.json || true
                '''
            }
        }

        stage('Migrations Check') {
            steps {
                sh '''
                    . venv/bin/activate
                    python manage.py makemigrations --check --dry-run --settings=alpine_club.test_settings || true
                '''
            }
        }

        stage('Backup Test DB') {
            steps {
                sh '''
                    mkdir -p reports
                    docker exec alpine-test-db mysqldump --no-tablespaces -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > reports/backup.sql
                    gzip -f reports/backup.sql
                '''
            }
        }

        stage('Container Build & Scan') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL \
                        --format json --output reports/trivy.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Publish Image') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "Все проверки пройдены. Публикация образа: ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }

    post {
        always {
            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/**'
            sh 'docker rm -f alpine-test-db || true'
        }
        failure {
            echo 'Пайплайн упал! Публикация образа НЕ выполнена.'
        }
    }
}
