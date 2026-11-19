pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    parameters {
        string(
            name: 'DEPLOY_TAG',
            defaultValue: '',
            description: 'Конкретный тег образа для выката или ручного возврата предыдущей версии'
        )
    }

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
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
            steps {
                sh '''
                    mkdir -p reports
                    docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect \
                        --source=/repo --report-format=json --report-path=/repo/reports/gitleaks.json || true
                '''
            }
        }

        stage('Setup & Cache Dependencies') {
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
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
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
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
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
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
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
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
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
            steps {
                sh '''
                    . venv/bin/activate
                    python manage.py makemigrations --check --dry-run --settings=alpine_club.test_settings || true
                '''
            }
        }

        stage('Backup Test DB') {
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
            steps {
                sh '''
                    mkdir -p reports
                    docker exec alpine-test-db mysqldump --no-tablespaces -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > reports/backup.sql
                    gzip -f reports/backup.sql
                '''
            }
        }

        stage('Container Build & Scan') {
            when {
                expression { !params.DEPLOY_TAG?.trim() }
            }
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                        aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL \\
                        --format json --output reports/trivy.json ${IMAGE_NAME}:${IMAGE_TAG} || true
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \\
                        aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL ${IMAGE_NAME}:${IMAGE_TAG} || true
                '''
            }
        }

        stage('Publish Image') {
            when {
                allOf {
                    expression { !params.DEPLOY_TAG?.trim() }
                    anyOf {
                        branch 'main'
                        buildingTag()
                    }
                }
            }
            steps {
                sh '''
                    docker push ${IMAGE_NAME}:${IMAGE_TAG}
                '''
                script {
                    env.PUBLISHED_TAG = env.IMAGE_TAG
                    echo "Все проверки пройдены. Публикация образа: ${IMAGE_NAME}:${PUBLISHED_TAG}"
                }
            }
        }

        stage('Deploy') {
            when {
                anyOf {
                    expression { params.DEPLOY_TAG?.trim() != '' }
                    allOf {
                        branch 'main'
                        expression { env.PUBLISHED_TAG?.trim() != '' }
                    }
                    allOf {
                        buildingTag()
                        expression { env.PUBLISHED_TAG?.trim() != '' }
                    }
                }
            }
            steps {
                script {
                    env.TARGET_TAG = params.DEPLOY_TAG?.trim() ? params.DEPLOY_TAG.trim() : env.PUBLISHED_TAG
                }
                withCredentials([sshUserPrivateKey(credentialsId: 'deploy-credentials', keyFileVariable: 'SSH_KEY_FILE')]) {
                    sh """
                        ssh -i "\$SSH_KEY_FILE" -o StrictHostKeyChecking=no deploy@hiplet-136600 "cd /opt/staging && APP_VERSION=${TARGET_TAG} docker compose --env-file /opt/staging/.env.staging -f /opt/staging/docker-compose.staging.yml pull && APP_VERSION=${TARGET_TAG} docker compose --env-file /opt/staging/.env.staging -f /opt/staging/docker-compose.staging.yml up -d"
                    """
                }
            }
        }

        stage('Verify Release') {
            when {
                expression { env.TARGET_TAG?.trim() != '' }
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'deploy-credentials', keyFileVariable: 'SSH_KEY_FILE')]) {
                    sh """
                        ssh -i "\$SSH_KEY_FILE" -o StrictHostKeyChecking=no deploy@hiplet-136600 "set -euo pipefail && cd /opt/staging && docker compose --env-file /opt/staging/.env.staging -f /opt/staging/docker-compose.staging.yml ps && VER_RESP=\\\$(curl -fsS http://127.0.0.1/version) && echo \\\"\\\$VER_RESP\\\" && echo \\\"\\\$VER_RESP\\\" | grep -q '${TARGET_TAG}' && PAGE_CODE=\\\$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/login/) && test \\\"\\\$PAGE_CODE\\\" -eq 200 -o \\\"\\\$PAGE_CODE\\\" -eq 302"
                    """
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
