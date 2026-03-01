# A basic Solas grammar extension for vscode

### Installing the basic Solas grammar using the `%USERPROFILE%\.vscode\extensions` path

- Create the folder:  
  `%USERPROFILE%\.vscode\extensions\solas\`

- Place the three files directly inside it:  
  `package.json`, `language-configuration.json`, `solas.tmLanguage.json`.

- Open that folder in VS Code (`File → Open Folder…`) so VS Code treats it as an extension project.

- Run **Developer: Reload Window** to make VS Code rescan the extensions directory; your Solas extension will now be recognised and loaded automatically.

- Open a `.solas` file in your main VS Code window to confirm syntax highlighting, comments, and bracket rules are active.

- When you update the grammar or configuration files, run **Developer: Reload Window** again to apply the changes.
