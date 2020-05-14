## Bias Detection in political statements on Twittter dataset.

Two parts:
  1. Finding the influential users in the network graph using Critical Node Detection Problem. This includes:
    
  * Serial implementation:
        #add stuff
  * Parallel implementation using OpenCL:
        #add stuff
  * Heterogenous implementation using OpenCL:
        #add stuff
        
  2. Topic Modelling of the tweets.


The requirements are:

* CMake 3.11 or better; 3.14+ highly recommended.
* A C++17 compatible compiler
* Git
* Doxygen (optional)

To configure:

```bash
cmake -S . -B build
```

Add `-GNinja` if you have Ninja.

To build:

```bash
cmake --build build
```

To test (`--target` can be written as `-t` in CMake 3.15+):

```bash
cmake --build build --target test
```

To build docs (requires Doxygen, output in `build/docs/html`):

```bash
cmake --build build --target docs
```

