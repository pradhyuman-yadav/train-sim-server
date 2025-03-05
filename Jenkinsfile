pipeline {
    agent any

    environment {
        TRAINSIM_SUPABASE_URL = credentials('TRAINSIM_SUPABASE_URL')
        TRAINSIM_SUPABASE_KEY = credentials('TRAINSIM_SUPABASE_KEY')
        IMAGE_NAME = "train-sim-server"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/pradhyuman-yadav/train-sim-server.git' // Your repo URL
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t train-sim-server:latest ."
                }
            }
        }
        
        stage('Run Docker Container') {
            steps {
                script {
                    // Stop/remove any old container (with proper error handling)
                    try {
                        sh "docker stop ${IMAGE_NAME}" // First try to stop gracefully
                    } catch (Exception e1) {
                        echo "Container '${IMAGE_NAME}' was not running.  Trying to remove..."
                    }
                    try {
                        sh "docker rm ${IMAGE_NAME}" // Then remove
                    } catch (Exception e2) {
                        echo "Container '${IMAGE_NAME}' did not exist or could not be removed. Continuing..."
                    }

                    // Run the new container, passing secrets as environment variables.
                    sh """
                    docker run -d --name ${IMAGE_NAME} -p 7000:7000 \\
                        -e TRAINSIM_SUPABASE_URL=${TRAINSIM_SUPABASE_URL} \\
                        -e TRAINSIM_SUPABASE_KEY=${TRAINSIM_SUPABASE_KEY} \\
                        ${IMAGE_NAME}:latest
                    """
                    // Removed --network=host.  This is generally NOT recommended unless absolutely necessary
                    // and can introduce security risks.  Port mapping (-p 7000:7000) is the preferred way.
                }
            }
        }
    }
}
