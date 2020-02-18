# Flink Stateful Functions Workshop 

## Setup Instructions

The following instructions guide you through the process of setting up a development environment for the purpose of developing, debugging, and executing solutions for the workshop.
Software Requirements:
Flink supports Linux, OS X, and Windows as development environments for Flink programs and local execution.
The following software is required for a Flink development setup and should be installed on your system:

* a JDK for Java 8 or Java 11 (a JRE is not sufficient; other versions of Java are not supported)
* Apache Maven 3.x
* Git
* Docker
* an IDE for Java (and/or Scala) development. We recommend IntelliJ, but Eclipse or Visual Studio Code can also be used so long as you stick to Java. For Scala you will need to use IntelliJ (and its Scala plugin).
Clone and build the exercises 

The flink-statefun-workshop project contains exercises, tests, and reference solutions for the programming exercises. Clone the flink-statefun-workshop project from Github and build it.

```bash
$ git clone https://github.com/ververica/flink-statefun-workshop.git
$ cd flink-statefun-workshop 
$ mvn install
$ docker-compose build 
```

If you haven’t done this before, at this point you’ll end up downloading all of the dependencies for this Flink project and the base docker image.
This usually takes a few minutes, depending on the speed of your internet connection.
