#!/bin/sh
# Install testing libs and run tests.
pip install \
    pytest==3.1.1 \
    pytest-cover==3.0.0 \
    pytest-flake8==0.6 \
    pyflakes==1.2.3 \
    flake8==3.0.0

# If RUN_INTEGRATION_TESTS is set, run integration tests.
echo "Run integration tests? ${RUN_INTEGRATION_TESTS}"
if [ "$RUN_INTEGRATION_TESTS" = "True" ] ; \
    then echo "Run all tests" && \
        python -m py.test \
            --cov-report term-missing \
            --cov=apputils \
            /app/halocelery/tests/style \
            /app/halocelery/tests/unit \
            /app/halocelery/tests/functional ;  \
    else echo Not running integration tests!. && \
        python -m py.test \
            /app/halocelery/tests/style \
            /app/halocelery/tests/unit ; \
    fi
