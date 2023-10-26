# P1 DTY: CV Parser


<!-- TABLE OF CONTENTS -->
<!--<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>
-->


Todo: USAGE + data + enhance description.

<!-- ABOUT THE PROJECT -->
## About The Project

This project is done in the context of the Digital Tech year Fall 2023 and consists in a CV parsing method that allows both to recover useful information in a database and asking questions over a pool of candidates using this database.


### Built With

The method is coded and Python and makes use of LangChain pipelines with GTP-3.5 running. 

## Getting Started

### Installation

1. Get a OpenAI API Key at [https://platform.openai.com](https://platform.openai.com)
2. Clone the repo:
   ```sh
   git clone https://github.com/falque/P1_RH.git
   ```
3. Install required Python packages:
   ```sh
   pip install -r requirements.txt
   ```
4. Create a .env file with your OpenAI API Key in the folder where you cloned the repo:
   ```sh
   touch .env
   echo "OPENAI_API_KEY=YOUR_OPENAI_API_KEY" >> .env
   ```
   where YOUR_OPENAI_API_KEY should be replaced by the key you got from OpenAI.

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- REPO STRUCTURE -->
## Repo structure

Main demo scripts can be found in ./src, utilities and loading methods are located in ./src/loading. Promptq to be fed to the LLM for each task are located in the .src/prompts folder.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

1. Connect to MySQL
2. Add the CVs to be parsed to a new ./data folder
3. [Optional] Run .src/fill_mysqldb.py to fill the database with the info parsed from the CVs
4. Run multi_gradio to ask questions on your pool of CVs

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- ROADMAP -->
<!--## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/othneildrew/Best-README-Template/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>-->



## Contributors

Mohammed Ali Belloum, Justine Falque, Sébastien Tran Tien, Emmanuel Zongo

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

<!--Your Name - [@your_twitter](https://twitter.com/your_username) - email@example.com

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>-->



<!-- ACKNOWLEDGMENTS -->
<!--## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* [Choose an Open Source License](https://choosealicense.com)
* [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)
* [Malven's Flexbox Cheatsheet](https://flexbox.malven.co/)
* [Malven's Grid Cheatsheet](https://grid.malven.co/)
* [Img Shields](https://shields.io)
* [GitHub Pages](https://pages.github.com)
* [Font Awesome](https://fontawesome.com)
* [React Icons](https://react-icons.github.io/react-icons/search)-->

<p align="right">(<a href="#readme-top">back to top</a>)</p>
