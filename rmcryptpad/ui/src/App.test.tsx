import { vi } from "vitest";
import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import "@testing-library/jest-dom/vitest";

vi.mock("./assets/cryptpad-mark.svg", () => ({
  default: "/ui/cryptpad/assets/cryptpad-mark.svg",
}));

import App from "./App";

test("renders an open button for CryptPad", () => {
  const { container } = render(
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
  expect(container.querySelector("img")).toHaveAttribute(
    "src",
    "/ui/cryptpad/assets/cryptpad-mark.svg",
  );
  expect(screen.getByRole("link", { name: /open cryptpad/i })).toHaveAttribute(
    "href",
    "https://mtls.cryptpad.example.invalid/login/",
  );
});
