pipeline {
    agent any

    environment {
        // Переменные для тестовой БД. 
        // ВАЖНО: Убедитесь, что alpine_club/test_settings.py читает эти переменные!
        DB_HOST     = '127.0.0.1'
        DB_PORT     = '3306'
        DB_NAME     = 'test_alpine_club'
        DB_USER     = 'testuser'
        DB_PASSWORD = 'testpassword'
        MYSQL_ROOT_PASSWORD = 'rootpassword'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python Env') {
            steps {
                // Создаем venv и ставим зависимости (включая coverage, ruff, bandit, если они в requirements.txt)
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Start Test DB') {
            steps {
                // Поднимаем контейнер с тестовой БД (Пункт 6)
                sh '''
                  docker rm -f alpine-test-db || true
                  docker run -d --name alpine-test-db \
                    -e MYSQL_DATABASE=${DB_NAME} \
                    -e MYSQL_USER=${DB_USER} \
                    -e MYSQL_PASSWORD=${DB_PASSWORD} \
                    -e MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD} \
                    -p 3306:3306 mysql:8.0
                  
                  echo "Waiting for MySQL to start..."
                  for i in $(seq 1 30); do
                    if docker exec alpine-test-db mysqladmin ping -h127.0.0.1 -uroot -p${MYSQL_ROOT_PASSWORD} --silent; then 
                      echo "MySQL is ready!"
                      break
                    fi
                    sleep 2
                  done
                '''
            }
        }

        stage('Quality (Style & Security)') {
            steps {
                // Вызов вашей make-команды (Пункт 5)
                sh '. venv/bin/activate && make quality'
            }
        }

        stage('Migrations') {
            steps {
                // Вызов вашей make-команды (Пункт 5)
                sh '. venv/bin/activate && make migrate'
            }
        }

        stage('Tests') {
            steps {
                // Вызов вашей make-команды (Пункт 5)
                sh '. venv/bin/activate && make test'
            }
            post {
                always {
                    // Сохранение отчетов, если они создаются (Пункт 7)
                    junit testResults: 'reports/*.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'coverage.xml, coverage_html/**', allowEmptyArchive: true
                }
            }
        }

        stage('Backup DB') {
            steps {
                // Ваша make-команда для бэкапа (Пункт 5)
                sh '. venv/bin/activate && make backup'
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backups/*.sql', allowEmptyArchive: true
                }
            }
        }
    }

    post {
        always {
            // Очистка контейнера
            sh 'docker rm -f alpine-test-db || true'
        }
    }
}
