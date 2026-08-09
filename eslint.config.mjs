import js from "@eslint/js";
import tseslint from "typescript-eslint";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";

export default tseslint.config(
  { ignores: ["out/**", "dist/**", "release/**", "node_modules/**"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    // TypeScript couvre déjà les symboles inconnus, mieux que la règle de base.
    files: ["**/*.{ts,tsx}"],
    rules: { "no-undef": "off" },
  },
  {
    files: ["src/renderer/**/*.{ts,tsx}", "test/**/*.{ts,tsx}"],
    plugins: { react, "react-hooks": reactHooks },
    languageOptions: {
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    settings: { react: { version: "detect" } },
    rules: {
      ...react.configs.flat.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // Le JSX ne nécessite plus l'import de React depuis la transformation automatique.
      "react/react-in-jsx-scope": "off",
      "react/prop-types": "off",
    },
  },
  {
    files: ["scripts/**/*.cjs"],
    languageOptions: {
      sourceType: "commonjs",
      globals: {
        require: "readonly",
        module: "writable",
        process: "readonly",
        console: "readonly",
        __dirname: "readonly",
      },
    },
    // Ces scripts tournent sous Node en CommonJS, avant tout bundling.
    rules: { "@typescript-eslint/no-require-imports": "off" },
  },
);
