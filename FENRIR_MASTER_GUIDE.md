# Fenrir Project Master Guide
## Complete Reference for Creating Error-Free Fenrir Projects

---

## Table of Contents
1. [Project Requirements Overview](#project-requirements-overview)
2. [Repository Structure](#repository-structure)
3. [Task Design Guidelines](#task-design-guidelines)
4. [Solvability Range 1-3](#solvability-range-1-3)
5. [Techniques for Hard Tasks](#techniques-for-hard-tasks)
6. [Things to Avoid](#things-to-avoid)
7. [Pipeline Error Prevention](#pipeline-error-prevention)
8. [Fuzzer Design](#fuzzer-design)
9. [Seed Corpus Strategy](#seed-corpus-strategy)
10. [Code Organization](#code-organization)
11. [Testing and Validation](#testing-and-validation)
12. [Common Pitfalls](#common-pitfalls)
13. [Examples and Templates](#examples-and-templates)
14. [Pre-Submission Checklist](#pre-submission-checklist)

---

## Project Requirements Overview

### Minimum Requirements
- **Lines of Code:** 15,000+ (recommended 20,000+)
- **Number of Bugs:** 25-30 (recommended 28-30)
- **Solvability Range:** All bugs must be Level 1-3
- **Fuzzers:** Minimum 4 (recommended 5-6)
- **Seed Corpus:** 10+ files per fuzzer
- **Repository:** Private, original work
- **Language:** Java 11 (or other supported languages)

### Quality Standards
- No knob bugs (adjustable thresholds/parameters)
- No magic byte routing
- No trivial fixes (single-line parameter changes)
- All bugs must be structural (require proper patches)
- Multiple unsafe paths per bug
- No explicit "BUG" comments or CVE references
- No symptom suppression

---

## Repository Structure

### Required Directory Structure
```
project-root/
├── src/
│   └── main/
│       └── java/
│           └── com/
│               └── yourcompany/
│                   ├── Module1.java
│                   ├── Module2.java
│                   ├── Module3.java
│                   └── ...
├── fuzz/
│   ├── Fuzzer1.java
│   ├── Fuzzer2.java
│   ├── Fuzzer3.java
│   ├── Fuzzer4.java
│   └── corpus/
│       ├── fuzzer1/
│       │   ├── seed1.bin
│       │   ├── seed2.bin
│       │   └── ...
│       ├── fuzzer2/
│       └── ...
├── .clusterfuzzlite/
│   ├── build.sh
│   └── Dockerfile (optional)
├── pom.xml (for Maven)
│   or build.gradle (for Gradle)
├── README.md
└── .gitignore
```

### Essential Files

#### .clusterfuzzlite/build.sh
```bash
#!/bin/bash
# Build script for fuzz targets
# Must compile all fuzzers to executable form

# Example for Java with Jazzer
set -e
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH=$JAVA_HOME/bin:$PATH

# Compile project
javac -d build -source 11 -target 11 \
    src/main/java/**/*.java \
    fuzz/*.java

# Build fuzzers with Jazzer
jazzer --cp=build \
    --instrumentation_includes=com.yourcompany.** \
    fuzz/Fuzzer1.java \
    fuzz/Fuzzer2.java \
    fuzz/Fuzzer3.java \
    fuzz/Fuzzer4.java
```

#### pom.xml (Maven)
```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.yourcompany</groupId>
    <artifactId>your-project</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <!-- Add necessary dependencies -->
    </dependencies>
</project>
```

#### .gitignore
```
build/
target/
*.class
*.jar
.DS_Store
.idea/
.vscode/
```

---

## Task Design Guidelines

### Core Principles

#### 1. Structural Bugs Only
**Definition:** Bugs that require understanding the code structure and logic, not just adjusting parameters.

**Examples of Structural Bugs:**
- State machine transition logic errors
- Race conditions in concurrent code
- Resource management issues
- Validation logic bypasses
- Cross-module interaction bugs
- Cache consistency issues
- Protocol parsing errors
- Authentication/authorization bypasses

**Examples of Knob Bugs (REJECTED):**
- Adjustable size limits
- Configurable timeouts
- Threshold parameters
- Default values
- Simple null checks

#### 2. Multiple Unsafe Paths
Each bug should have multiple ways to trigger it, not just one specific input.

**Implementation:**
- Bug should be reachable through different code paths
- Different input sequences should trigger the bug
- Bug should not require exact input matching

#### 3. No Explicit Bug Indicators
**REJECTED:**
```java
// BUG: This is a bug
// TODO: Fix this vulnerability
// CVE-2024-XXXXX
```

**ACCEPTED:**
```java
// No comments indicating bugs
// Code looks like normal implementation
```

---

## Solvability Range 1-3

### Level 1 Bugs (33-40% of total)
**Characteristics:**
- Require basic understanding of the module
- Single-module scope
- 1-2 code locations to fix
- 10-30 minutes to solve
- Simple but not trivial

**Examples:**
- Missing null checks in critical paths
- Off-by-one errors in loops
- Incorrect condition logic
- Missing validation in setters
- Simple state management errors

**Level 1 Example:**
```java
// Bug: Missing null check in getter
public byte[] getData() {
    return data.clone(); // Should check if data is null first
}

// Fix:
public byte[] getData() {
    if (data == null) {
        return new byte[0];
    }
    return data.clone();
}
```

### Level 2 Bugs (42-50% of total)
**Characteristics:**
- Require understanding multiple components
- Cross-module interactions
- 2-4 code locations to fix
- 30-60 minutes to solve
- Moderate complexity

**Examples:**
- Race conditions between modules
- Cache consistency across components
- State synchronization issues
- Protocol validation bypasses
- Resource allocation/deallocation mismatches

**Level 2 Example:**
```java
// Bug: Race condition in cache update
public void updateCache(String key, byte[] value) {
    CacheEntry existing = cache.get(key);
    if (existing != null) {
        stats.currentSize.addAndGet(-existing.size); // Race: size might change
    }
    cache.put(key, new CacheEntry(key, value));
    stats.currentSize.addAndGet(value.length);
}

// Fix: Use atomic operations or proper locking
public void updateCache(String key, byte[] value) {
    cacheLock.writeLock().lock();
    try {
        CacheEntry existing = cache.get(key);
        if (existing != null) {
            stats.currentSize.addAndGet(-existing.size);
        }
        cache.put(key, new CacheEntry(key, value));
        stats.currentSize.addAndGet(value.length);
    } finally {
        cacheLock.writeLock().unlock();
    }
}
```

### Level 3 Bugs (15-25% of total)
**Characteristics:**
- Require root-cause analysis
- Complex state transitions
- 4-6 code locations to fix
- 60-120 minutes to solve
- High complexity

**Examples:**
- Complex state machine logic errors
- Subtle protocol parsing bugs
- Multi-layer validation bypasses
- Complex resource lifecycle issues
- Authentication token handling

**Level 3 Example:**
```java
// Bug: State machine auto-transition to ERROR on invalid event
public boolean transition(StateEvent event) {
    ConnectionState newState = TRANSITION_TABLE.get(currentState).get(event);
    
    if (newState == null) {
        if (currentState == ConnectionState.ERROR_DETECTED) {
            return false;
        }
        newState = ConnectionState.ERROR_DETECTED; // Auto-transition bug
    }
    
    currentState = newState;
    return true;
}

// Fix: Proper error handling without auto-transition
public boolean transition(StateEvent event) {
    ConnectionState newState = TRANSITION_TABLE.get(currentState).get(event);
    
    if (newState == null) {
        return false; // Reject invalid transitions
    }
    
    currentState = newState;
    return true;
}
```

### REJECTED Solvability Levels

#### Level 0 (Trivial Bugs)
**REJECTED Examples:**
```java
// Too simple - single character change
if (x > 0) { } // Change to if (x >= 0) { }

// Simple parameter default
int timeout = config.timeout != null ? config.timeout : 5000; // Default value

// Basic null check
if (data == null) return; // Trivial fix
```

#### Level 4-5 (Architectural Changes)
**REJECTED Examples:**
```java
// Requires complete redesign
// Needs architectural changes
// Requires new components
// Requires major refactoring
```

---

## Techniques for Hard Tasks

### 1. State Machine Complexity
**Technique:** Create complex state transitions with subtle bugs.

**Implementation:**
```java
public class StateMachine {
    private State currentState;
    private Map<State, Map<Event, State>> transitionTable;
    
    // Bug: Auto-transition on invalid event
    public boolean transition(Event event) {
        State newState = transitionTable.get(currentState).get(event);
        if (newState == null) {
            newState = State.ERROR; // Bug: auto-transition
        }
        currentState = newState;
        return true;
    }
    
    // Bug: State visit counter not reset properly
    public void reset() {
        currentState = State.INITIAL;
        // Bug: Forgot to reset counters
    }
}
```

### 2. Race Conditions
**Technique:** Introduce subtle race conditions in concurrent code.

**Implementation:**
```java
public class ResourceManager {
    private final AtomicLong available;
    
    // Bug: Non-atomic check-and-allocate
    public boolean allocate(long amount) {
        if (available.get() >= amount) {
            // Race: Another thread might allocate here
            available.addAndGet(-amount);
            return true;
        }
        return false;
    }
    
    // Fix: Use compareAndSet
    public boolean allocate(long amount) {
        while (true) {
            long current = available.get();
            if (current < amount) return false;
            if (available.compareAndSet(current, current - amount)) {
                return true;
            }
        }
    }
}
```

### 3. Validation Bypass
**Technique:** Create validation logic that can be bypassed.

**Implementation:**
```java
public class ProtocolValidator {
    // Bug: Order of validation checks allows bypass
    public boolean validate(ProtocolMessage msg) {
        if (msg.getVersion() < MIN_VERSION) return false;
        if (msg.getPayload().length > MAX_SIZE) return false;
        // Bug: Checksum validation after size check allows crafted messages
        if (!validateChecksum(msg)) return false;
        return true;
    }
    
    // Fix: Validate checksum first
    public boolean validate(ProtocolMessage msg) {
        if (!validateChecksum(msg)) return false;
        if (msg.getVersion() < MIN_VERSION) return false;
        if (msg.getPayload().length > MAX_SIZE) return false;
        return true;
    }
}
```

### 4. Cache Consistency
**Technique:** Introduce cache consistency bugs across operations.

**Implementation:**
```java
public class CacheManager {
    private Map<String, CacheEntry> cache;
    private Map<String, Long> accessOrder;
    
    // Bug: Access order not updated on hit
    public byte[] get(String key) {
        CacheEntry entry = cache.get(key);
        if (entry != null) {
            // Bug: Forgot to update access order
            return entry.data.clone();
        }
        return null;
    }
    
    // Bug: Size tracking not updated on replacement
    public void put(String key, byte[] value) {
        CacheEntry existing = cache.get(key);
        if (existing != null) {
            // Bug: Size not decremented before replacement
            cache.put(key, new CacheEntry(key, value));
            stats.size.addAndGet(value.length);
        }
    }
}
```

### 5. Resource Lifecycle
**Technique:** Introduce bugs in resource allocation/deallocation.

**Implementation:**
```java
public class ConnectionPool {
    // Bug: Connection not properly closed on eviction
    public void evictIdleConnections() {
        for (Connection conn : connections.values()) {
            if (conn.getIdleTime() > timeout) {
                connections.remove(conn.getId());
                // Bug: Forgot to close connection
            }
        }
    }
    
    // Bug: Resource leak on exception
    public Connection acquire() {
        Connection conn = createConnection();
        if (!conn.connect()) {
            // Bug: Connection not cleaned up on failure
            throw new ConnectionException("Failed to connect");
        }
        return conn;
    }
}
```

### 6. Authentication/Authorization
**Technique:** Subtle auth/authz bypasses.

**Implementation:**
```java
public class SessionManager {
    // Bug: Token validation timing attack
    public boolean validateToken(String token) {
        String expected = getExpectedToken();
        if (token.length() != expected.length()) return false;
        
        for (int i = 0; i < token.length(); i++) {
            if (token.charAt(i) != expected.charAt(i)) {
                return false; // Bug: Early return allows timing attack
            }
        }
        return true;
    }
    
    // Bug: Permission check after action
    public void performAction(String user, String action) {
        executeAction(action); // Bug: Action executed before permission check
        if (!hasPermission(user, action)) {
            throw new SecurityException("Unauthorized");
        }
    }
}
```

### 7. Protocol Parsing
**Technique:** Subtle parsing bugs in protocol handlers.

**Implementation:**
```java
public class ProtocolParser {
    // Bug: Fragment validation allows overlap
    public boolean validateFragment(Fragment frag) {
        if (frag.offset < 0) return false;
        if (frag.offset + frag.length > frag.totalSize) return false;
        // Bug: Allows overlapping fragments
        return true;
    }
    
    // Bug: Integer overflow in size calculation
    public int calculateTotalSize(List<Fragment> fragments) {
        int total = 0;
        for (Fragment f : fragments) {
            total += f.length; // Bug: No overflow check
        }
        return total;
    }
}
```

### 8. Cross-Module Bugs
**Technique:** Bugs that span multiple modules.

**Implementation:**
```java
// Module1: SessionManager
public class SessionManager {
    public void createSession(String userId) {
        String token = generateToken();
        sessions.put(token, new Session(userId));
        // Bug: Token not stored in token registry
    }
}

// Module2: TokenValidator
public class TokenValidator {
    public boolean validate(String token) {
        // Bug: Checks token registry instead of session map
        return tokenRegistry.contains(token);
    }
}
```

---

## Things to Avoid

### CRITICAL: Never Do These

#### 1. Knob Bugs
**REJECTED:**
```java
// Adjustable threshold
if (data.length > MAX_SIZE) { } // MAX_SIZE is a knob

// Configurable parameter
int timeout = config.timeout != null ? config.timeout : 5000;

// Size limit
if (count > 1000) { } // 1000 is a knob
```

#### 2. Magic Byte Routing
**REJECTED:**
```java
// Magic byte determines which module to call
if (data[0] == 0x41) {
    moduleA.process(data);
} else if (data[0] == 0x42) {
    moduleB.process(data);
}
```

#### 3. Explicit Bug Comments
**REJECTED:**
```java
// BUG: This is a bug
// TODO: Fix this
// FIXME: Vulnerability
// CVE-2024-XXXXX
```

#### 4. Symptom Suppression
**REJECTED:**
```java
try {
    dangerousOperation();
} catch (Exception e) {
    // Bug: Swallowing exceptions
}
```

#### 5. Trivial Fixes
**REJECTED:**
```java
// Single character change
if (x > 0) { } → if (x >= 0) { }

// Simple null check
if (data == null) return;

// Default value
int value = param != null ? param : 0;
```

### WARNINGS: Be Careful With These

#### 1. Too Simple Bugs
**WARNING:**
```java
// Too simple - might be Level 0
public String getName() {
    return name; // Should clone
}
```

#### 2. Too Complex Bugs
**WARNING:**
```java
// Too complex - might be Level 4+
// Requires architectural redesign
// Needs new components
```

#### 3. Single-Path Bugs
**WARNING:**
```java
// Only one way to trigger
public void process(byte[] data) {
    if (data.length == 42) { // Very specific condition
        // Bug here
    }
}
```

#### 4. Blocked Bugs
**WARNING:**
```java
// Bug blocked by validation
public void process(byte[] data) {
    if (validate(data)) { // Validation prevents reaching bug
        // Bug here
    }
}
```

---

## Pipeline Error Prevention

### Build Errors

#### Error: Build Failed
**Prevention:**
```bash
# Test build locally before submission
./.clusterfuzzlite/build.sh

# Verify compilation
javac -d build -source 11 -target 11 src/**/*.java fuzz/**/*.java

# Check for missing dependencies
mvn dependency:tree
```

**Common Causes:**
- Missing dependencies in pom.xml
- Wrong Java version
- Compilation errors in source
- Incorrect build script

#### Error: Fuzzer Not Found
**Prevention:**
```bash
# Verify all fuzzers are listed in build.sh
cat .clusterfuzzlite/build.sh | grep Fuzzer

# Check fuzzer files exist
ls fuzz/*.java

# Verify fuzzer has required method
grep -l "fuzzerTestOneInput" fuzz/*.java
```

### Fuzzer Errors

#### Error: No Crashes Found
**Prevention:**
1. Ensure bugs are in fuzzer-reachable code paths
2. Add direct calls to bug-containing modules
3. Expand seed corpus
4. Remove blocking validation checks

**Example:**
```java
@FuzzTest
public void fuzzerTestOneInput(byte[] data) {
    // Direct call to module with bug
    ModuleWithBug module = new ModuleWithBug();
    module.process(data); // Bug should be reachable here
    
    // Call other modules
    AnotherModule another = new AnotherModule();
    another.handle(data);
}
```

#### Error: Magic Byte Routing Detected
**Prevention:**
```java
// WRONG: Magic byte routing
if (data[0] == 0x41) {
    moduleA.process(data);
}

// CORRECT: Always call all modules
ModuleA moduleA = new ModuleA();
ModuleB moduleB = new ModuleB();
moduleA.process(data);
moduleB.process(data);
```

### Quality Errors

#### Error: Knob Bugs Detected
**Prevention:**
- Remove all adjustable thresholds
- Remove parameter defaults
- Replace with structural bugs

**Example:**
```java
// WRONG: Knob bug
if (data.length > MAX_SIZE) { }

// CORRECT: Structural bug
if (data.length > calculateMaxSize()) { } // Dynamic calculation
```

#### Error: Too Few Bugs Triggered
**Prevention:**
1. Add bugs in all modules called by fuzzers
2. Expand fuzzer coverage to more modules
3. Add more seed files
4. Ensure bugs are in high-traffic methods

**Target:**
- 25-30 bugs total
- All bugs in 1-3 solvability range
- All bugs reachable through fuzzers

#### Error: Solvability Issues
**Prevention:**
- Remove Level 0 bugs (trivial)
- Remove Level 4-5 bugs (architectural)
- Target distribution: 40% Level 1, 45% Level 2, 15% Level 3

---

## Fuzzer Design

### Fuzzer Requirements

#### 1. Minimum 4 Fuzzers
Each fuzzer should target different aspects of the codebase.

#### 2. Fuzzer Structure
```java
import com.code_intelligence.jazzer.api.FuzzedDataProvider;
import com.code_intelligence.jazzer.api.FuzzerSecurityIssueLow;

public class ExampleFuzzer {
    public static void fuzzerTestOneInput(byte[] data) {
        try {
            // Create instances of modules
            Module1 module1 = new Module1();
            Module2 module2 = new Module2();
            
            // Process input
            module1.process(data);
            module2.process(data);
            
            // Call other methods
            if (data.length > 10) {
                module1.handle(data);
            }
            
        } catch (Exception e) {
            // Expected exceptions
        }
    }
}
```

#### 3. Fuzzer Coverage Rules
- Each fuzzer should call 4-6 different modules
- All modules should be covered by at least one fuzzer
- High-traffic methods should be called by multiple fuzzers
- No magic byte routing

#### 4. Fuzzer Examples

**Protocol Parser Fuzzer:**
```java
public class ProtocolParserFuzzer {
    public static void fuzzerTestOneInput(byte[] data) {
        try {
            // Parse protocol message
            ProtocolMessage message = ProtocolMessage.deserialize(data);
            
            // Validate
            ProtocolValidator validator = new ProtocolValidator();
            validator.validate(message);
            
            // Process through codec
            BinaryCodec codec = new BinaryCodec();
            codec.encode(message.getPayload());
            
            // Compression
            CompressionLayer compression = new CompressionLayer();
            compression.compress(message.getPayload());
            
        } catch (Exception e) {
            // Expected
        }
    }
}
```

**Session Manager Fuzzer:**
```java
public class SessionManagerFuzzer {
    public static void fuzzerTestOneInput(byte[] data) {
        try {
            SessionManager manager = new SessionManager();
            
            // Create session
            String sessionId = "sess_" + Math.abs(data[0]);
            manager.createSession(sessionId, "user");
            
            // Authenticate
            if (data.length > 5) {
                manager.authenticateSession(sessionId, "token");
            }
            
            // Cache operations
            CacheManager cache = new CacheManager();
            cache.put(sessionId, data);
            cache.get(sessionId);
            
        } catch (Exception e) {
            // Expected
        }
    }
}
```

---

## Seed Corpus Strategy

### Seed Corpus Requirements

#### 1. Minimum 10 Files Per Fuzzer
Each fuzzer should have at least 10 seed files covering different scenarios.

#### 2. Seed File Types
- Valid inputs
- Edge cases
- Boundary conditions
- Error cases
- Random data

#### 3. Seed File Generation

**Valid Inputs:**
```bash
# Create valid protocol messages
echo -ne "\x41\x42\x43\x44" > fuzz/corpus/fuzzer1/valid1.bin
echo -ne "\x00\x01\x02\x03" > fuzz/corpus/fuzzer1/valid2.bin
```

**Edge Cases:**
```bash
# Boundary conditions
echo -ne "\x00\x00\x00\x00" > fuzz/corpus/fuzzer1/edge1.bin
echo -ne "\xFF\xFF\xFF\xFF" > fuzz/corpus/fuzzer1/edge2.bin
```

**Random Data:**
```bash
# Random bytes
dd if=/dev/urandom of=fuzz/corpus/fuzzer1/random1.bin bs=64 count=1
```

#### 4. Seed Corpus Structure
```
fuzz/corpus/
├── fuzzer1/
│   ├── valid1.bin
│   ├── valid2.bin
│   ├── edge1.bin
│   ├── edge2.bin
│   ├── random1.bin
│   ├── random2.bin
│   └── ...
├── fuzzer2/
│   └── ...
└── ...
```

---

## Code Organization

### Module Design

#### 1. Module Structure
Each module should be:
- Self-contained
- Well-documented (but no bug comments)
- 200-500 lines of code
- Multiple methods with bugs

#### 2. Module Example
```java
package com.yourcompany.project;

import java.util.*;
import java.util.concurrent.*;

public class ResourceManager {
    // Configuration
    private final Map<ResourceType, ResourcePool> pools;
    private final AtomicInteger allocationId;
    private final ReentrantLock lock;
    
    // Statistics
    private final ResourceStats stats;
    
    public ResourceManager(ResourceManagerConfig config) {
        this.pools = new ConcurrentHashMap<>();
        this.allocationId = new AtomicInteger(0);
        this.lock = new ReentrantLock();
        this.stats = new ResourceStats();
        initializePools(config);
    }
    
    // Methods with bugs
    public ResourceAllocation allocate(ResourceType type, long amount) {
        // Bug here
    }
    
    public void deallocate(String allocationId) {
        // Bug here
    }
    
    // Helper methods
    private void initializePools(ResourceManagerConfig config) {
        // Implementation
    }
    
    // Inner classes
    public static class ResourceAllocation {
        // Bug here
    }
    
    public static class ResourcePool {
        // Bug here
    }
}
```

#### 3. Module Count
- Minimum 10 modules
- Recommended 15-20 modules
- Each module should have 2-3 bugs

### Code Size Requirements

#### 1. Total Lines: 15,000+
**Breakdown:**
- Core modules: 10,000 lines
- Fuzzers: 1,000 lines
- Tests: 2,000 lines
- Configuration: 500 lines
- Documentation: 1,500 lines

#### 2. Per Module: 200-500 lines
**Example:**
```java
// 300-line module with 3 bugs
public class CacheManager {
    // 50 lines: Configuration
    // 100 lines: Core methods with bugs
    // 50 lines: Helper methods
    // 50 lines: Inner classes
    // 50 lines: Statistics
}
```

---

## Testing and Validation

### Pre-Submission Testing

#### 1. Build Test
```bash
./.clusterfuzzlite/build.sh
```

#### 2. Compilation Test
```bash
javac -d build -source 11 -target 11 src/**/*.java fuzz/**/*.java
```

#### 3. Fuzzer Test
```bash
# Test each fuzzer individually
jazzer --cp=build fuzz/Fuzzer1.java
jazzer --cp=build fuzz/Fuzzer2.java
jazzer --cp=build fuzz/Fuzzer3.java
jazzer --cp=build fuzz/Fuzzer4.java
```

#### 4. Seed Corpus Test
```bash
# Verify seed files exist
ls fuzz/corpus/*/

# Count seed files
find fuzz/corpus -name "*.bin" | wc -l
```

#### 5. Bug Count Verification
```bash
# Count potential bug locations
grep -r "if\|while\|for" src/ | wc -l

# Verify no explicit bug comments
grep -r "BUG\|TODO\|FIXME\|CVE" src/
```

### Local Fuzzing

#### 1. Quick Fuzzing Test
```bash
# Run fuzzer for 60 seconds
jazzer --cp=build -max_total_time=60 fuzz/Fuzzer1.java
```

#### 2. Crash Detection
```bash
# Check for crashes
ls -la crashes/
```

---

## Common Pitfalls

### 1. Insufficient Code Coverage
**Problem:** Bugs not reachable through fuzzers.

**Solution:**
- Add direct calls to bug-containing modules in fuzzers
- Expand fuzzer coverage to more modules
- Ensure all modules are covered by at least one fuzzer

### 2. Too Simple Bugs
**Problem:** Bugs are too trivial (Level 0).

**Solution:**
- Add complexity to bug logic
- Require understanding multiple components
- Make bugs require multi-site fixes

### 3. Too Complex Bugs
**Problem:** Bugs require architectural changes (Level 4-5).

**Solution:**
- Keep bugs within existing architecture
- Require understanding but not redesign
- Focus on logic errors, not design flaws

### 4. Knob Bugs
**Problem:** Adjustable parameters/thresholds.

**Solution:**
- Remove all configurable values
- Replace with structural bugs
- Make bugs require proper patches

### 5. Magic Byte Routing
**Problem:** Input determines which module to call.

**Solution:**
- Always call all modules
- Remove conditional module selection
- Ensure all code paths are reachable

### 6. Blocked Bugs
**Problem:** Validation prevents reaching bugs.

**Solution:**
- Remove blocking validation checks
- Ensure bugs are in high-traffic paths
- Add bugs before validation

### 7. Single-Path Bugs
**Problem:** Only one way to trigger bug.

**Solution:**
- Add multiple trigger paths
- Make bugs reachable through different inputs
- Add bugs in common operations

---

## Examples and Templates

### Level 1 Bug Template
```java
// Missing validation in setter
public void setValue(int value) {
    // Bug: No validation
    this.value = value;
}

// Fix: Add validation
public void setValue(int value) {
    if (value < 0 || value > MAX_VALUE) {
        throw new IllegalArgumentException("Invalid value");
    }
    this.value = value;
}
```

### Level 2 Bug Template
```java
// Race condition in cache
public void update(String key, byte[] value) {
    CacheEntry existing = cache.get(key);
    if (existing != null) {
        stats.size.addAndGet(-existing.size); // Race condition
    }
    cache.put(key, new CacheEntry(key, value));
    stats.size.addAndGet(value.length);
}

// Fix: Add proper locking
public void update(String key, byte[] value) {
    lock.writeLock().lock();
    try {
        CacheEntry existing = cache.get(key);
        if (existing != null) {
            stats.size.addAndGet(-existing.size);
        }
        cache.put(key, new CacheEntry(key, value));
        stats.size.addAndGet(value.length);
    } finally {
        lock.writeLock().unlock();
    }
}
```

### Level 3 Bug Template
```java
// State machine auto-transition bug
public boolean transition(Event event) {
    State newState = transitionTable.get(currentState).get(event);
    
    if (newState == null) {
        if (currentState == State.ERROR) {
            return false;
        }
        newState = State.ERROR; // Bug: Auto-transition
    }
    
    currentState = newState;
    return true;
}

// Fix: Proper error handling
public boolean transition(Event event) {
    State newState = transitionTable.get(currentState).get(event);
    
    if (newState == null) {
        return false; // Reject invalid transitions
    }
    
    currentState = newState;
    return true;
}
```

### Fuzzer Template
```java
import com.code_intelligence.jazzer.api.FuzzedDataProvider;

public class ModuleFuzzer {
    public static void fuzzerTestOneInput(byte[] data) {
        try {
            // Create module instances
            Module1 module1 = new Module1();
            Module2 module2 = new Module2();
            
            // Process input through all modules
            module1.process(data);
            module2.handle(data);
            
            // Call additional methods
            if (data.length > 10) {
                module1.validate(data);
            }
            
        } catch (Exception e) {
            // Expected exceptions
        }
    }
}
```

---

## Pre-Submission Checklist

### Repository
- [ ] Repository is private
- [ ] Repository contains original work
- [ ] No renamed public projects
- [ ] Proper directory structure
- [ ] All required files present

### Code Quality
- [ ] 15,000+ lines of code
- [ ] 25-30 bugs total
- [ ] All bugs in 1-3 solvability range
- [ ] No knob bugs
- [ ] No magic byte routing
- [ ] No explicit bug comments
- [ ] No symptom suppression

### Fuzzers
- [ ] Minimum 4 fuzzers
- [ ] All fuzzers build successfully
- [ ] All fuzzers have fuzzerTestOneInput method
- [ ] All modules covered by fuzzers
- [ ] No magic byte routing in fuzzers

### Seed Corpus
- [ ] 10+ seed files per fuzzer
- [ ] Valid inputs included
- [ ] Edge cases included
- [ ] Random data included
- [ ] Seed files in correct directories

### Build
- [ ] .clusterfuzzlite/build.sh exists
- [ ] Build script compiles all fuzzers
- [ ] Build succeeds locally
- [ ] No compilation errors
- [ ] No missing dependencies

### Testing
- [ ] Build tested locally
- [ ] Fuzzers tested locally
- [ ] Seed corpus verified
- [ ] Bug count verified
- [ ] No explicit bug comments found

### Documentation
- [ ] README.md present
- [ ] Build instructions clear
- [ ] No bug comments in code
- [ ] Professional code style

---

## Final Notes

### Success Factors
1. **Original Work:** Must be your own code, not copied or renamed
2. **Structural Bugs:** All bugs must require proper patches
3. **Proper Coverage:** All modules must be reachable through fuzzers
4. **Right Difficulty:** All bugs in 1-3 solvability range
5. **No Shortcuts:** No knob bugs, magic byte routing, or trivial fixes

### Common Success Patterns
- Start with a solid architecture
- Add bugs incrementally
- Test each bug for reachability
- Verify fuzzer coverage
- Expand seed corpus
- Test build locally
- Submit only when ready

### When to Submit
- All checklist items complete
- Local fuzzing finds crashes
- Build succeeds consistently
- No compilation errors
- Repository is private
- Code is original work

---

**This guide is based on extensive experience with Fenrir project submissions and covers all lessons learned from successful and rejected projects. Follow these guidelines to maximize your chances of acceptance.**
