pipeline {
    agent any

    stages {
        stage('Build and Test') {
            steps {
                // Build and run unit tests
                bat 'python backend/test_predict.py'
            }
        }

        stage('User Acceptance') {
            when {
                branch 'release'
            }
            steps {
                // Prompt user for confirmation
                // input {
                //     message "Do you want to release this version to production?"
                //     ok "Yes"
                //     submitter "No"
                // }

                // Merge release branch to main
                bat 'git merge origin/release'

                // Push to Dockerhub
                bat 'docker build -t my-docker-image .'
                bat 'docker push my-docker-image'

                // Push changes to main branch
                bat 'git push origin main'
            }
        }
    }
}