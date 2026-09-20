# DocVerify — Demo Script (3-Minute Presentation)

> **Format**: Video presentation for Bharat Builds Tour (First Commit)  
> **Target Duration**: 03:00 (180 seconds)  
> **Key Thesis**: *"Bedrock never decides whether a document is valid — it only explains a decision our deterministic engine already made. And the raw document is destroyed before you finish reading the verdict."*

---

## Storyboard & Script Breakdown

| Time | Visual / Screen Action | Spoken Line (Verbatim) | Proven Edge Case |
|------|------------------------|-------------------------|------------------|
| **0:00 – 0:20** | Show real application rejection slip: Name spelling mismatch on certificate. | *"Every year, lakhs of Indian students are rejected from scholarships not because they're ineligible, but because of a single spelling difference — like Ashish vs Aashish. DocVerify checks the application before submission."* | Problem Context |
| **0:20 – 0:45** | Select **Post-Matric Scholarship** profile. Upload grid shows required documents. | *"DocVerify evaluates the entire application, not just an isolated file. Here is the Post-Matric Scholarship profile with four required documents."* | Multi-document profile context |
| **0:45 – 1:15** | Upload Academic Marksheet in place of Income Certificate. Pipeline runs live. | *"Our ingestion gate checks magic bytes and PDF encryption. Next, our classifier scores weighted signals deterministically — without an LLM. It detects this is a Marksheet (score 85), not an Income Certificate (score 5), rejecting it with an actionable error."* | **Edge Case E02** (Wrong doc type) |
| **1:15 – 1:45** | Upload genuine Aadhaar (`Kunal Borse`) + wrong Marksheet (`Rahul Borse`). | *"Now we run cross-document identity verification. Rule NM-06 fires: Rahul Borse vs Kunal Borse is a hard identity mismatch. Status: 🔴 NOT READY."* | **Edge Case E05** (Identity mismatch) |
| **1:45 – 2:10** | Click into finding. Toggle explanation from English to **हिन्दी**. | *"Notice our architectural boundary: Bedrock did not decide this mismatch. Our pure Python engine decided. Bedrock only generates this plain-language guidance in the student's native language."* | **Edge Case E10 & E13** (AI boundary & i18n) |
| **2:10 – 2:30** | Test subtle variation: `Kunal Bapurao Borse` vs `Kunal Borse` or `Ashish` vs `Aashish`. | *"DocVerify does not cry wolf. Transliteration folding and token subset logic recognize this is the same applicant. Verdict: 🟢 MATCH via legitimate variation."* | **Edge Case E06** (False-positive protection) |
| **2:30 – 2:45** | Click **Replace Document** with correct Marksheet → Re-verify → Status transitions to 🟢 **READY**. | *"The student fixes the document in seconds, re-verifies, and achieves a clean READY verdict with zero stale concurrency overwrites."* | **Edge Case E15** (Re-verification) |
| **2:45 – 3:00** | Point to the Lifecycle Strip: `[✓ Uploaded] -> [✓ Validated] -> [✓ Verified] -> [✓ Result Stored] -> [✓ Raw Document Deleted]`. Show CloudWatch / S3 404. | *"Best of all, the raw documents are encrypted, verified, and deleted immediately — confirmed by a 404 verification check. The document is gone. The audit trail remains."* | **Edge Case E17** (Document destruction) |
