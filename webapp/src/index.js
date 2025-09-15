import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

if (module.hot) {
  module.hot.accept();
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
  