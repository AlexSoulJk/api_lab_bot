pipeline {
    agent any
    stages {
        stage('Backup') {
            steps {
                script {
                    if (fileExists('backup_database.py')) {
                        sh 'cd C:/Users/Hp/PycharmProjects/api_bot_lab1'
                        sh './venv/Scripts/activate'
                        sh 'start /B python3 ./backup_database.py'
                    } else {
                        echo 'Файл backup_database.py не найден'
                    }
                }
            }
        }
    }
}