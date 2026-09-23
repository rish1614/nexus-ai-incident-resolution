import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "../src/App";

vi.mock("../src/services/api", () => ({
  fetchHealth: vi.fn().mockResolvedValue({ status: "healthy", service: "nexus-backend" }),
}));

describe("App", () => {
  it("renders the NEXUS landing page heading", () => {
    render(<App />);
    expect(screen.getByText("NEXUS")).toBeInTheDocument();
  });

  it("shows a backend connectivity indicator", () => {
    render(<App />);
    expect(screen.getByText(/Backend API:/)).toBeInTheDocument();
  });
});
