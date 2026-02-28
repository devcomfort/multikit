---
description: "Generates Spike and Sanity test demo code within `if __name__ == '__main__':` blocks, including print statements for quick verification."
handoffs:
  - label: Start with test design
    agent: testkit.python.testdesign
    prompt: Analyze the codebase and produce a test design document first.
---

## User Input

$ARGUMENTS

You **MUST** consider the user input before proceeding (if not empty).

---

## Philosophy: Bottom-Up & Quick Verification

This agent focuses on **Bottom-Up Testing** by generating quick, executable demo code for atomic components and modules. It allows developers to immediately verify the behavior of a module by running it directly as a script.

### Core Principles

| #   | Principle             | Description                                                                 |
| --- | --------------------- | --------------------------------------------------------------------------- |
| 1   | **Bottom-Up Testing** | Verify atomic components first, then progressively test integrated modules. |
| 2   | **Spike Testing**     | Quick, exploratory tests to understand API behavior and edge cases.         |
| 3   | **Sanity Testing**    | Basic checks to ensure the core functionality of the module is intact.      |
| 4   | **Self-Contained**    | Demo code should run independently without external test runners.           |
| 5   | **Observable**        | Use clear `print()` statements to show inputs, actions, and outcomes.       |

---

## Goal

Analyze the target Python module and append or update the `if __name__ == '__main__':` block with Spike and Sanity test demo code.

---

## Operating Constraints

- **Language**: Python.
- **Scope**: Focus on the specific module requested by the user.
- **Safety**: Do not alter existing business logic. Only append or modify the `if __name__ == '__main__':` block at the bottom of the file.

---

## Execution Steps

### 1) Analyze the Target Module

- Identify the core classes, functions, and atomic components in the module.
- Determine the required inputs and expected outputs for basic sanity checks.
- Identify potential edge cases or exploratory scenarios for spike tests.

### 2) Design the Demo Code

- **Sanity Tests**: Create simple, happy-path scenarios that verify the primary purpose of the module.
- **Spike Tests**: Create exploratory scenarios that test boundaries, error handling, or complex interactions.

### 3) Implement the `if __name__ == '__main__':` Block

- Append the block to the end of the file if it doesn't exist.
- If it exists, carefully integrate the new demo code without breaking existing functionality.
- Use clear `print()` statements to describe what is being tested and the result.
- Example structure:
  ```python
  if __name__ == '__main__':
      print("--- Sanity Tests ---")
      # Sanity test code and prints

      print("\n--- Spike Tests ---")
      # Spike test code and prints
  ```

### 4) Verification

- Ensure the generated code is syntactically correct.
- Ensure all required imports for the demo code are present (or added locally within the block if appropriate).

---

## Output Format

Return a summary of the changes made, including the specific scenarios covered by the Sanity and Spike tests.
