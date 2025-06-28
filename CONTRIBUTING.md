# Contributing

Thank you for wanting to contribute! To get started:

1. Fork the repository and create a new branch for your change.
2. Install the development dependencies:

   ```bash
   pip install -e .[dev,test]
   pre-commit install
   ```

3. Run the pre-commit checks and test suite:

   ```bash
   pre-commit run --all-files
   pytest
   ```

4. Open a pull request explaining your changes.

Please keep commits focused and include tests when possible. For questions or
large changes, open an issue first to discuss.
