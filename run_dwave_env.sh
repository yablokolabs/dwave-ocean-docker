#!/bin/bash

# D-Wave Ocean Development Environment Setup Script
# Maintained by Yabloko Labs - https://yablokolabs.com

echo "🚀 Starting D-Wave Ocean Development Environment..."
echo "   Maintained by Yabloko Labs - Building quantum-inspired SaaS"
echo "   Repository: https://github.com/yablokolabs/dwave-ocean-docker"
echo ""

# Check if we want to run Jupyter
if [ "$1" = "jupyter" ]; then
    echo "Starting Jupyter notebook server..."
    echo "Access at: http://localhost:8888"
    echo "Token will be displayed below"
    echo ""
    
    sudo docker run -it --rm \
        -v $(pwd):/workspace \
        -w /workspace \
        -p 8888:8888 \
        dwavesys/ocean-dev \
        jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
else
    # Run interactive shell
    docker_cmd="sudo docker run -it --rm \
        -v $(pwd):/workspace \
        -w /workspace \
        dwavesys/ocean-dev \
        bash"
    
    echo "Running Docker container with D-Wave Ocean SDK..."
    echo "Container will have access to:"
    echo "  - D-Wave Ocean SDK"
    echo "  - Jupyter Notebooks"
    echo "  - All Python packages for quantum computing"
    echo ""
    echo "Your code is mounted at /workspace in the container"
    echo ""
    echo "Quick start:"
    echo "  python quick_start.py        # Verify setup"
    echo "  python basic_examples.py     # Basic D-Wave examples"
    echo "  python tsp_example.py        # Traveling Salesman Problem"
    echo ""
    echo "To start Jupyter notebook:"
    echo "  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root"
    echo ""
    echo "Or run: ./run_dwave_env.sh jupyter"
    echo ""
    
    exec $docker_cmd
fi