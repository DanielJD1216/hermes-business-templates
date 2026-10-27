---
name: customer-onboarding
description: "Use when the old customer-onboarding skill is installed. Switch to dooing-onboarding."
version: 0.27.0
license: MIT
platforms: [linux, macos]
---

# Renamed to dooing-onboarding

This guide is now the `dooing-onboarding` skill. Its baseline, progress checker
and upgrade notes moved with it unchanged, and the owner's private progress
record stays valid.

Switch on the agent host, then continue the setup:

1. `hermes skills install skills-sh/DanielJD1216/hermes-business-templates/skills/dooing-onboarding`
2. Check that `hermes skills list` shows `dooing-onboarding`.
3. `hermes skills uninstall customer-onboarding`
4. Continue with the `dooing-onboarding` skill and the same private progress
   record. Apply its upgrade notes for every version newer than the record's
   `Template revision`.
