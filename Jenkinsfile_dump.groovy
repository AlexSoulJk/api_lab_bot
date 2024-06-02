pipeline {
    agent any

    stages {
        stage('Download git repo') {
            steps {
                echo '===============downloading git repo==================='
                script {
                    try {
                        if (isUnix()) {
                            sh 'rm -rf Reminder_Bot'
                            sh 'git clone --depth=1 https://github.com/AlexSoulJk/api_lab_bot.git'
                            sh 'rm -rf api_lab_bot/.git*'
                        } else {
                            bat 'powershell -Command "Get-ChildItem -Path .\\* -Recurse | Remove-Item -Force -Recurse"'
                            bat 'git clone --depth=1 https://github.com/AlexSoulJk/api_lab_bot.git'
                            bat 'powershell Remove-Item api_lab_bot/.git* -Recurse -Force'
                        }
                    } catch (Exception e) {
                        error "Failed to download git repo: ${e.getMessage()}"
                    }
                }
                echo '===============git repo downloaded==================='
            }
        }

        stage('Getting creds and env variables') {
            steps {
                echo '===============getting env variables==================='
                withCredentials([file(credentialsId: 'ENVD', variable: 'ENV'),
                file(credentialsId: 'CREDS1', variable: 'CREDS'),
                file(credentialsId: 'TOKEN1', variable: 'TOKEN')]) {
                    script {
                        try {
                            if (isUnix()) {
                                sh 'cp $ENV ./api_lab_bot/.env'
                                sh 'cp $CREDS ./api_lab_bot/credentials.json'
                                sh 'cp $TOKEN ./api_lab_bot/token.json'
                            } else {
                                bat 'powershell Copy-Item %ENV% -Destination ./api_lab_bot/.env'
                                bat 'powershell Copy-Item %CREDS% -Destination ./api_lab_bot/credentials.json'
                                bat 'powershell Copy-Item %TOKEN% -Destination ./api_lab_bot/token.json'
                            }
                        } catch (Exception e) {
                            error "Failed to get creds and env variables: ${e.getMessage()}"
                        }
                    }
                }
                echo '===============got creds and env variables==================='
            }
        }
        stage('Backup') {
            steps {
                script {
                    if (fileExists('backup_database.py')) {
                        sh 'start /B python3 backup_database.py'
                    } else {
                        echo 'Файл backup_database.py не найден'
                    }
                }
            }
        }
    }
}