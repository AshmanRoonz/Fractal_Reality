import "./styles.css";
import shellHtml from "./game-shell.html?raw";

document.title = "Last Ship Sailing";
document.body.innerHTML = shellHtml.trim();

void import("./game.js");
