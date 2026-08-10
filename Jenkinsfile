pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['qa', 'uat', 'prod'],
            description: 'Environment to execute tests'
        )

        choice(
            name: 'TEST_MARKER',
            choices: ['smoke', 'sanity', 'regression'],
            description: 'Pytest marker to execute'
        )

        choice(
            name: 'BROWSER',
            choices: ['chromium', 'firefox', 'webkit'],
            description: 'Browser for Playwright execution'
        )

        booleanParam(
            name: 'HEADED',
            defaultValue: false,
            description: 'Run browser in headed mode'
        )

        booleanParam(
            name: 'REPORT',
            defaultValue: true,
            description: 'Generate Allure report'
        )

        booleanParam(
            name: 'TESTRAIL',
            defaultValue: true,
            description: 'Publish results to TestRail'
        )
    }

    environment {
        PYTHON_EXE = '.venv\\Scripts\\python.exe'

        TESTRAIL_BASE_URL = 'https://opencart.testrail.io'
        TESTRAIL_PROJECT_ID = '2'
        TESTRAIL_SUITE_ID = ''

        /*
         Use this only if Jenkins cannot find Allure commandline.
         Example:
         ALLURE_COMMAND = 'C:\\Users\\Supriya\\AppData\\Roaming\\npm\\allure.cmd'
        */
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                bat """
                if not exist .venv (
                    python -m venv .venv
                )

                %PYTHON_EXE% -m pip install --upgrade pip
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                bat """
                %PYTHON_EXE% -m pip install -r requirements.txt
                %PYTHON_EXE% -m playwright install %BROWSER%
                """
            }
        }

        stage('Prepare Report Folders') {
            steps {
                bat """
                if not exist reports mkdir reports
                if not exist reports\\logs mkdir reports\\logs
                if not exist reports\\junit mkdir reports\\junit
                if not exist reports\\allure-results mkdir reports\\allure-results
                if not exist reports\\allure-reports mkdir reports\\allure-reports
                """
            }
        }

        stage('Verify Tools') {
            steps {
                bat """
                %PYTHON_EXE% --version
                %PYTHON_EXE% -m pytest --version
                %PYTHON_EXE% -m playwright --version
                """
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def markerArg = params.TEST_MARKER == 'all'
                        ? ''
                        : "-m ${params.TEST_MARKER}"

                    def headedArg = params.HEADED
                        ? '--headed'
                        : ''

                    def reportFlag = params.REPORT
                        ? 'true'
                        : 'false'

                    def testrailFlag = params.TESTRAIL
                        ? 'true'
                        : 'false'

                    def testCommand = """
                    %PYTHON_EXE% -m pytest ${markerArg} ^
                        --env=${params.TEST_ENV} ^
                        --browser ${params.BROWSER} ^
                        ${headedArg} ^
                        --report=${reportFlag} ^
                        --testrail=${testrailFlag} ^
                        --junitxml=reports\\junit\\pytest-results.xml ^
                        -s
                    """

                    if (params.TESTRAIL) {
                        withCredentials([
                            usernamePassword(
                                credentialsId: 'testrail-api',
                                usernameVariable: 'TESTRAIL_USERNAME',
                                passwordVariable: 'TESTRAIL_API_KEY'
                            )
                        ]) {
                            bat testCommand
                        }
                    } else {
                        bat testCommand
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Archiving framework reports and logs...'

            archiveArtifacts(
                artifacts: 'reports/logs/*.log,reports/junit/*.xml,reports/allure-results/**,reports/allure-reports/**',
                allowEmptyArchive: true
            )

            junit(
                testResults: 'reports/junit/*.xml',
                allowEmptyResults: true
            )
        }
    }
}