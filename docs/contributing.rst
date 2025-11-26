============
Contributing
============

We welcome contributions to psqlc!

Development Setup
=================

1. Fork the repository:

   .. code-block:: bash

      git clone https://github.com/cumulus13/psqlc.git
      cd psqlc

2. Create virtual environment:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # Linux/macOS
      # or
      venv\\Scripts\\activate  # Windows

3. Install development dependencies:

   .. code-block:: bash

      pip install -e ".[dev]"

Running Tests
=============

.. code-block:: bash

   pytest tests/
   pytest --cov=psqlc tests/

Code Style
==========

We use Black for code formatting:

.. code-block:: bash

   black psqlc.py
   flake8 psqlc.py

Building Documentation
======================

.. code-block:: bash

   cd docs
   make html
   # View at docs/_build/html/index.html

Pull Requests
=============

1. Create a feature branch:

   .. code-block:: bash

      git checkout -b feature/your-feature

2. Make your changes

3. Add tests if applicable

4. Ensure all tests pass

5. Submit pull request

Guidelines
==========

* Follow PEP 8 style guide
* Add docstrings to new functions
* Update documentation for new features
* Include examples in documentation
* Write clear commit messages

Bug Reports
===========

Submit bug reports at: https://github.com/cumulus13/psqlc/issues

Include:

* Operating system and version
* Python version
* PostgreSQL version
* Steps to reproduce
* Expected vs actual behavior
* Error messages

Feature Requests
================

We're open to new features! Please open an issue to discuss before implementing.

License
=======

By contributing, you agree that your contributions will be licensed under the MIT License.