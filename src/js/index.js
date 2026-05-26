import React from "react";
import * as ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/browser";
import * as application from "./lib/application";

// SENTRY_DSN baked at build time by webpack DefinePlugin.
if (process.env.SENTRY_DSN) {
  Sentry.init({ dsn: process.env.SENTRY_DSN });
}

ReactDOM.createRoot(document.getElementById("root")).render(<application.Interface />);
