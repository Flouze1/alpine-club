pipeline {
    agent any

    environment {
        // Переменные для тестовой БД
        DB_HOST     = '127.0.0.1'
        DB_PORT     = '3306'
        DB_NAME     = 'test_alpine_club'
        DB_USER     = 'testuser'
        DB_PASSWORD = 'testpassword'
        MYSQL_ROOT_PASSWORD = 'rootpassword'
        
        // Имя образа для локального Docker Hub
        IMAGE_NAME  = 'localhost:5000/alpine-club'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Setup Python Env') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
                
                // Устанавливаем инструменты, которые нужны для make quality и make test
                sh '. venv/bin/activate && pip install cryptography ruff bandit coverage'
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
                sh '. venv/bin/activate && make quality'
            }
        }

        stage('Migrations') {
            steps {
                sh '. venv/bin/activate && make migrate'
            }
        }

        stage('Tests') {
            steps {
                sh '. venv/bin/activate && make test'
            }
            post {
                always {
                    junit testResults: 'reports/*.xml', allowEmptyResults: true
                    archiveArtifacts artifacts: 'coverage.xml, coverage_html/**', allowEmptyArchive: true
                }
            }
        }

        stage('Backup DB') {
            steps {
                // Исправлено: mysqldump выполняется ВНУТРИ контейнера с БД
                sh '''
                  docker exec alpine-test-db mysqldump \
                    -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} > backup.sql
                  gzip -f backup.sql
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'backup.sql.gz', allowEmptyArchive: true
                }
            }
        }

        stage('Container Check') {
            steps {
                // Проверка Dockerfile и сборка тестового образа (Пункт 5)
                sh 'docker build -t alpine-club:check .'
            }
        }

        stage('Build & Publish') {
            // Публикация ТОЛЬКО для ветки main (Пункт 10)
            when {
                branch 'main'
            }
            steps {
                script {
                    // Получаем короткий SHA коммита для тега (Пункт 9)
                    def sha = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    def image = "${IMAGE_NAME}:${sha}"
                    
                    // Собираем финальный образ
                    sh "docker build -t ${image} ."
                    
                    // Отправляем в локальный Docker Hub (если у вас настроен registry:2 на порту 5000)
                    // Если registry без пароля, логин не нужен
                    sh "docker push ${image}"
                    echo "Successfully published: ${image}"
                }
            }
        }
    }

    post {
        always {
            // Очистка контейнера после завершения
            sh 'docker rm -f alpine-test-db || true'
        }
        failure {
            echo 'Пайплайн упал. Публикация образа отменена (если была).'
        }
    }
}
