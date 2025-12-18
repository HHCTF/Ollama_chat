This is a python script that uses Ollama LLMs into a tkinker app thats all local and easy to use.
Firstly to start run `git clone https://github.com/HHCTF/Ollama_chat.git`
then after (you need docker to run this next command) run `sudo docker build -t ollama_chat.py .`
after that you need to give execution permission to a script to let the AIs work, `chmod +x ~/GithubRepos/Ollama_chat/run_ollama_gui.sh`
Finally, you can run `~/GithubRepos/Ollama_chat./run_ollama_gui.sh`
If you want you can to your bashrc or zshrc and add an alias to make it similar to open.
Thank you for reading and using this script and I hope you find it useful like how I did!


EDIT: 12/17/25 make sure to download the nessecary ollama models for this script to work. Required models: `ollama pull mistral:latest` `ollama pull dolpin-mixtral` (Dolphin Mixtral may take a long time to pull so beware.) `ollama pull llama3`
