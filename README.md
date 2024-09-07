# AlefTransformer
Transforming React HML Project JSON structure to Alef Educational Platform Suitable XML Structure

---

# AlefTransformer Django Project

This repository contains the source code for the AlefTransformer Django project.

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- Git

### Install Essential Dependencies
   ```bash
   sudo apt-get install -y build-essential && sudo apt-get install -y checkinstall && sudo apt-get install -y libreadline-gplv2-dev && sudo apt-get install -y libncursesw5-dev && sudo apt-get install -y libssl-dev && sudo apt-get install -y libsqlite3-dev && sudo apt-get install -y tk-dev && sudo apt-get install -y libgdbm-dev && sudo apt-get install -y libc6-dev && sudo apt-get install -y libbz2-dev && sudo apt-get install -y zlib1g-dev && sudo apt-get install -y openssl && sudo apt-get install -y libffi-dev && sudo apt-get install -y python3-dev && sudo apt-get install -y python3-setuptools && sudo apt-get install -y wget
   ```

### If MacOS then run following command to resolve certificate error
   ```bash
   open /Applications/Python\ 3.7/Install\ Certificates.command
   ```

### Installation Steps

1. **Clone the repository**

    ```bash
    git clone https://github.com/krisskad/AlefTransformer.git
    cd AlefTransformer
    ```

2. **Create a Virtual Environment**

    Using virtualenv
    ```bash
    python3 -m venv env
   ```
    Activate the virtual environment\
    If On Windows

   ```bash
    .\env\Scripts\activate
   ```
   If On Unix or MacOS
   ```bash
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