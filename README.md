# Module 3 – Internet-Based Vessel Cost Estimation

## 1. Objective

Module 3 is intended for situations where the client has a short vessel specification/brief and needs a vessel-level cost estimate within a limited response time.

The proposed solution uses the uploaded vessel specification together with publicly available internet information to identify comparable vessels, collect supporting cost evidence, perform specification-level matching, apply applicable cost adjustments, and generate a reviewable vessel-level estimate.

The objective is not to search the internet for the price of every individual component. The primary objective is to retrieve and use comparable **vessel-level cost information**.

---

## 2. Proposed End-to-End Approach

```text
Vessel Parameters + Specification PDF
                |
                v
       Specification Extraction
                |
                v
       Structured Vessel Profile
                |
                v
      Targeted Internet Search
                |
                v
       Candidate Vessel Discovery
                |
                v
        Source Verification
                |
                v
   Specification-Level Matching
                |
                v
         Cost Evidence Extraction
                |
                v
          Cost Normalization
                |
                v
       Cost / Country / Year
            Adjustments
                |
                v
       Comparable Vessel Analysis
                |
                v
       Vessel-Level Cost Estimate
                |
                v
       Evidence & Assumptions
                |
                v
        Client User Review/Edit
                |
                v
          Final Report
