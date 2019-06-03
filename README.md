# Graphgen

A library for random graph generation.

## Installation

Graphgen requires:

- UNIX system (such as Linux and macOS);
- Python 3 or more recent;
- [NetworkX](https://github.com/networkx/networkx), [NumPy](https://github.com/numpy/numpy) and [SciPy](https://github.com/scipy/scipy);
- [nauty](http://pallini.di.uniroma1.it).

### Automatic installation (with pip)

For the automatic installation, follows the steps below.

1. Open a terminal and clone the repository.
  
    ```sh
    git clone https://github.com/Nico-Salamone/graphgen.git
    ```

1. Change directory (`cd`) to the Graphgen directory.
  
    ```sh
    cd ./graphgen/
    ```
    
1. Run the following command in your terminal.

    ```sh
    pip3 install -e .
    ```

### Manual installation

For the manual installation, follows the steps below.

1. Open a terminal and clone the repository.
  
    ```sh
    git clone https://github.com/Nico-Salamone/graphgen.git
    ```

1. Change directory (`cd`) to the Graphgen directory.
  
    ```sh
    cd ./graphgen/
    ```

1. Run the following commands in your terminal.
    ```sh
    # Install Python dependencies.
    pip3 install networkx
    pip3 install numpy
    pip3 install scipy
    
    # Compile nauty (C program).
    make clean -C graphgen/resources/nauty
    make -C graphgen/resources/nauty
    
    # Install Graphgen.
    cp -r graphgen 'your-python-path'/site-packages/graphgen/
    # Replace 'your-python-path' by the Python installation path.
    # On Linux, it is either "/usr/lib/python3.X" or "~/.local/lib/python3.X" (replace '3.X' by the version of your Python).
    # On macOS, it is "/Library/Frameworks/Python.framework/Versions/3.X/lib/python3.X" (replace '3.X' by the version of your Python).
    ```

### Note about Windows

It is probably possible to install Graphgen on Windows 10 or newer with the Linux Bash shell. To do this, you will need to install the `make` command beforehand. Unfortunately, I have not a computer with Windows installed, so I can not test if it works.