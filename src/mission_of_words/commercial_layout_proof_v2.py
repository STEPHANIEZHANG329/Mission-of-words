"""Internal engineering geometry PDF. NOT an Owner-facing product.

Shim around the factory-based internal geometry builder. Procedural art
is a layout stand-in only. Paid GPT2 stays closed.
"""

from mission_of_words.internal_geometry import PDF, REPORT, build

__all__ = ["PDF", "REPORT", "build"]


if __name__ == "__main__":
    build()
