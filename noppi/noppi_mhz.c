#define _GNU_SOURCE  // Required for pthread_setaffinity_np
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <stdlib.h>
#include <pthread.h>
#include <string.h>

#define NOP_DELAY_MS 100
#define CLOCK_SPEED_MHZ 45.625

void delay_ms(int milliseconds) {
    usleep(milliseconds * 1000); // usleep uses microseconds, so convert milliseconds to microseconds
}

void *nop_thread(void *arg) {
    int core_id = *(int *)arg;
    
    // Set thread affinity to the specified core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    
    pthread_t current_thread = pthread_self();
    if (pthread_setaffinity_np(current_thread, sizeof(cpu_set_t), &cpuset) != 0) {
        perror("pthread_setaffinity_np");
        exit(EXIT_FAILURE);
    }
    
    // Run NOP instructions indefinitely
    while (1) {
        int count = 0;
        clock_t start_time = clock();
        
        // Run NOP instructions for 100 milliseconds
        while (((clock() - start_time) * 1000 / CLOCKS_PER_SEC) < NOP_DELAY_MS) {
            asm("nop");
            count++;
        }
        
        // Calculate MHz (NOPs count / CLOCK_SPEED_MHZ)
        double mhz = count / CLOCK_SPEED_MHZ;
        
        // Output the count of NOPs executed and MHz
        printf("Thread on core %d executed %d NOPs in %d ms (%.2f MHz)\n", core_id, count, NOP_DELAY_MS, mhz);
        
        delay_ms(1000); // Delay for 1 second before the next iteration
    }
    
    return NULL;
}

int main() {
    char input[10];
    int core_id;
    
    // Prompt user to enter core ID
    printf("Enter CPU core ID: ");
    fgets(input, sizeof(input), stdin);
    
    // Remove newline character from input
    input[strcspn(input, "\n")] = 0;
    
    // Convert input to integer
    core_id = atoi(input);
    
    // Launch thread on specified core
    pthread_t thread;
    pthread_attr_t attr;
    pthread_attr_init(&attr);
    
    // Create thread
    if (pthread_create(&thread, &attr, nop_thread, &core_id) != 0) {
        perror("pthread_create");
        exit(EXIT_FAILURE);
    }
    
    // Join thread (this should not normally be reached in this infinite loop scenario)
    if (pthread_join(thread, NULL) != 0) {
        perror("pthread_join");
        exit(EXIT_FAILURE);
    }
    
    return 0;
}
