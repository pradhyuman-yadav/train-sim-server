pipeline {
    agent any

    environment {
        TRAINSIM_SUPABASE_URL = credentials('TRAINSIM_SUPABASE_URL')
        TRAINSIM_SUPABASE_KEY = credentials('TRAINSIM_SUPABASE_KEY')
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
                    sh """
                    docker build \\
                        --build-arg TRAINSIM_SUPABASE_URL="${TRAINSIM_SUPABASE_URL}" \\
                        --build-arg TRAINSIM_SUPABASE_KEY="${TRAINSIM_SUPABASE_KEY}" \\
                        -t train-sim-server:latest .
                    """
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Stop/remove any old container (with proper error handling)
                    try {
                        sh 'docker rm -f train-sim-server'
                    } catch (Exception e) {
                        echo "Container 'train-sim-server' did not exist or could not be removed. Continuing..."
                        // Optionally, log the full exception:  echo e.getMessage()
                    }

                    // Run the new container, using --env-file for runtime secrets
                    sh """
                    docker run --network host -v /proc:/host_proc -e HOST_PROC=/host_proc -d \\
                        --name train-sim-server \\
                        -p 7000:7000 \\
                        -e TRAINSIM_SUPABASE_URL="${TRAINSIM_SUPABASE_URL}" \\
                        -e TRAINSIM_SUPABASE_KEY="${TRAINSIM_SUPABASE_KEY}" \\
                        train-sim-server:latest
                    """
                }
            }
        }
    }
}