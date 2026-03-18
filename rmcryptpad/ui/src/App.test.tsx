import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import "@testing-library/jest-dom/vitest";

import App from "./App";

test("renders an open button for CryptPad", () => {
  render(
    <App
      data={{
        url: "https://mtls.cryptpad.example.invalid",
        sandbox_url: "https://mtls.sandbox.cryptpad.example.invalid",
      }}
      meta={{ callsign: "VIRTA-1", theme: "light" }}
    />,
  );

  expect(screen.getByText("VIRTA-1")).toBeInTheDocument();
  expect(
    screen.getByText("https://mtls.sandbox.cryptpad.example.invalid"),
  ).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /open cryptpad/i })).toHaveAttribute(
    "href",
    "https://mtls.cryptpad.example.invalid",
  );
});
