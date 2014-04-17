#include <unistd.h>
#include <iostream>

pid_t shared_state = 0;

int main(int argc, char** argv, char** envp) {
    std::cout << "before fork" << std::endl;
    pid_t pid = fork();
    std::cout << "after fork pid " << pid << std::endl;
    if (pid != 0) {
        shared_state = pid;
    } else {
        usleep(1000000);
    }
    std::cout << "pid " << pid << " says shared state is " << shared_state << std::endl;
    return 0;
}
