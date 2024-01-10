# AlefTransformer
Transforming JSON structure to Alef XML Sructure

---

# AlefTransformer Django Project

This repository contains the source code for the AlefTransformer Django project.

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- Git

### Installation Steps

1. **Clone the repository**

    ```bash
    git clone https://github.com/krisskad/AlefTransformer.git
    cd AlefTransformer
    ```

2. **Create a Virtual Environment**

    ```bash
    # Using virtualenv
    python3 -m venv env
    # Activate the virtual environment
    # On Windows
    .\env\Scripts\activate
    # On Unix or MacOS
    source env/bin/activate
    ```

3. **Install Dependencies**

    ```bash
    sudo apt-get install python3-lxml
    sudo apt-get install libxml2-dev libxslt-dev python3-dev
    pip install -r requirements.txt
    ```

4. **Run the Development Server**

    ```bash
    python manage.py runserver
    ```

7. **Access the Application**

    Open your web browser and visit `http://127.0.0.1:8000/`


## Input Directory Structure
```
templates_dir
   app
      structure.json
      audio.json
      en_text.json
      images.json
      video.json
common_dir
   templates, 
      config, 
         glossary.json
         glossaryImages.json
         templateImages.json
         text.json
```

### Contributors

- [krishna kadam](https://github.com/krisskad/)