pipeline {
    agent any

    stages {
        stage('Backup') {
            steps {
                script {
                    if (fileExists('backup_database.py')) {
                        if (!fileExists('.env')) {
                            echo 'Файл .env не найден'
                        }
                        sh 'start /B python3 backup_database.py'
                    } else {
                        echo 'Файл backup_database.py не найден'
                    }
                }
            }
        }
    }
}