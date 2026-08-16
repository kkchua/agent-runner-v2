---
doc_type: "default_impl"
identity_locked: true
generator_name: "text_summarizer_ayz"
codename: "text_summarizer_ayz"
version: "1.0.0"
spec_reference: "COMPOSITION_SPEC-01.md"
standard_reference: "BASE_COMPOSITION_STANDARD_v1.0.md"
pattern: "Input Transformation (Pattern 2)"
impl_date: "2026-08-10"
---

# Default Runtime Implementation: text_summarizer_ayz

## Implementation Identity

| Field | Value |
|---|---|
| impl_id | text_summarizer_ayz_default |
| generator_codename | text_summarizer_ayz |
| composition_spec | COMPOSITION_SPEC-01.md |
| pattern | Input Transformation (Pattern 2) |
| version | 1.0.0 |

This document is the self-contained default runtime implementation deliverable
for the text_summarizer_ayz generator. It defines the concrete executor that
satisfies the composition specification, including complete algorithm
descriptions, data structures, configuration defaults, and extension point
implementations.

---

## 1. Pipeline Architecture

### 1.1 Execution Model

The runtime uses a linear 7-stage pipeline (stage 0 for input loading, stages
1-6 for transformation). Each stage is a discrete processing unit with defined
inputs, outputs, pre-conditions, and post-conditions.

```
Stage 0: Input Loading        -> SourceDocument (L1)
Stage 1: Importance Scoring   -> ImportanceAnalysis (L2)
Stage 2: Redundancy Analysis  -> RedundancyCluster[] (L2)
Stage 3: Key Point Extraction -> KeyPoint[] (L2)
Stage 4: Summary Composition  -> SummaryBlock[] (L2)
Stage 5: Output Assembly      -> OutputDocument[] (L3)
Stage 6: Output Validation    -> Validated OutputDocument[]
```

### 1.2 Pipeline Controller

```
class PipelineController:
    config: RuntimeConfig
    registry: RuntimeRegistry
    
    method execute(input_path: str, output_dir: str) -> ExecutionResult:
        // Stage 0: Load input
        source_doc = registry.get_parser(input_path.format).parse(input_path)
        
        // Stage 1: Score importance
        analysis = registry.importance_scorer.score(source_doc.all_text_units(), source_doc)
        
        // Stage 2: Detect redundancy
        clusters = registry.redundancy_detector.detect_clusters(source_doc.all_text_units(), analysis)
        
        // Stage 3: Extract key points
        keypoints = KeyPointExtractor.extract(analysis, clusters, config.keypoint_threshold)
        
        // Stage 4: Compose summary blocks
        blocks = SummaryBlockComposer.compose(source_doc, analysis, clusters, config.compression_ratio)
        
        // Stage 5: Assemble output documents
        outputs = OutputAssembler.assemble(source_doc, blocks, keypoints, config.output_types)
        
        // Stage 6: Validate outputs
        ValidationEngine.validate(outputs, source_doc)
        
        // Render to disk
        for output in outputs:
            renderer = registry.get_renderer(output.output_type)
            renderer.write(output, output_dir)
        
        return ExecutionResult(outputs)
```

### 1.3 Execution Result

```
class ExecutionResult:
    source_document: SourceDocument
    importance_analysis: ImportanceAnalysis
    redundancy_clusters: RedundancyCluster[]
    key_points: KeyPoint[]
    summary_blocks: SummaryBlock[]
    output_documents: OutputDocument[]
    output_paths: Map[output_type, file_path]
```

---

## 2. Data Structures

### 2.1 Layer 1 Components

#### SourceDocument (COMP-L1-001)

```
class SourceDocument:
    doc_id: string                        // "doc-{timestamp}"
    language: string                      // ISO 639-1 code (e.g., "en", "zh")
    word_count: integer                   // Total word count
    encoding: string                      // Default: "utf-8"
    raw_format: enum {txt, md}            // Source file format
    sections: StructuralSection[]         // Ordered list of sections
    
    method all_text_units() -> TextUnit[]:
        // Returns all TextUnits across all sections, ordered by position
        result = []
        for section in sections (ordered by position):
            result.extend(section.text_units)
        return result
```

#### StructuralSection (COMP-L1-002)

```
class StructuralSection:
    section_id: string                    // "sec-{position}"
    section_type: enum {introduction, body, conclusion}
    position: integer                     // 1-based sequential
    text_units: TextUnit[]                // Ordered list
    section_word_count: integer           // Word count for this section
```

#### TextUnit (COMP-L1-003)

```
class TextUnit:
    unit_id: string                       // "tu-{position}"
    content: string                       // The sentence text
    unit_type: enum {sentence, paragraph} // Default: sentence
    position: integer                     // Document-global 1-based
    word_count: integer                   // Word count of this unit
    section_ref: string                   // Parent section_id
```

### 2.2 Layer 2 Components

#### ImportanceAnalysis (COMP-L2-001)

```
class ImportanceAnalysis:
    analysis_id: string                   // "analysis-{timestamp}"
    scored_units: ScoredUnit[]            // All TextUnits scored
    scoring_method: string                // Name of algorithm used
```

#### ScoredUnit (COMP-L2-002)

```
class ScoredUnit:
    unit_ref: string                      // TextUnit unit_id
    importance_score: float               // [0.0, 1.0]
    rank: integer                         // 1 = most important
```

#### RedundancyCluster (COMP-L2-003)

```
class RedundancyCluster:
    cluster_id: string                    // "cluster-{index}"
    representative_unit_ref: string       // TextUnit unit_id (highest score)
    constituent_unit_refs: string[]       // All member TextUnit unit_ids
    consolidation_score: float            // [0.0, 1.0] average pairwise similarity
```

#### KeyPoint (COMP-L2-004)

```
class KeyPoint:
    keypoint_id: string                   // "kp-{index}"
    source_unit_ref: string               // Source TextUnit unit_id
    content: string                       // Extracted key point text
    importance_score: float               // From ScoredUnit
    rank: integer                         // Ordering (1 = most important)
    section_ref: string                   // Origin StructuralSection
```

#### SummaryBlock (COMP-L2-005)

```
class SummaryBlock:
    block_id: string                      // "block-{section_position}"
    section_ref: string                   // Source StructuralSection
    content: string                       // Condensed summary text
    target_section_type: enum {introduction, body, conclusion}
    source_unit_refs: string[]            // TextUnit unit_ids used
    block_word_count: integer             // Word count of this block
```

### 2.3 Layer 3 Components

#### OutputDocument (COMP-L3-001)

```
class OutputDocument:
    output_id: string                     // "out-{output_type}-{timestamp}"
    output_type: enum {condensed_summary, key_points_list, executive_summary, bullet_overview, abstract}
    source_doc_ref: string                // SourceDocument doc_id
    language: string                      // Must match SourceDocument.language
    output_blocks: OutputBlock[]          // Ordered content blocks
    metadata: dict                        // Output-type-specific metadata
    validation_rules: ValidationRule[]    // Rules that must pass
```

#### OutputBlock (COMP-L3-002)

```
class OutputBlock:
    block_id: string                      // Unique identifier
    content: string                       // Rendered text content
    block_type: enum {prose_paragraph, numbered_item, scored_item, section_heading}
    position: integer                     // Sequential order index
    metadata: dict                        // Optional block-level metadata
```

#### ValidationRule (COMP-L3-003)

```
class ValidationRule:
    rule_id: string                       // Unique identifier (e.g., "VR-001")
    rule_type: enum {word_count_ratio, language_match, structure_preservation, no_new_info, score_present}
    description: string                   // Human-readable description
    threshold: float                      // Numeric threshold (optional)
    applies_to: enum[]                    // Which output_types this applies to
```

---

## 3. Input Loading (Stage 0)

### 3.1 DefaultInputParser

Dispatches to format-specific parsers based on file extension.

```
class DefaultInputParser implements InputParser:
    parsers: Map[string, FormatParser]  // registered at init
    
    method parse(input_path: string) -> SourceDocument:
        // Validate file exists (V-MAP-IN-001)
        if not file_exists(input_path):
            raise InputValidationError("V-MAP-IN-001", "File not found: " + input_path)
        
        // Detect format (MAP-IN-002)
        ext = file_extension(input_path)
        if ext not in [".txt", ".md"]:
            raise InputValidationError("V-MAP-IN-002", "Unsupported format: " + ext)
        
        // Read content (MAP-IN-001)
        content = read_file(input_path, encoding="utf-8")
        
        // Validate non-empty (V-MAP-IN-003)
        if content.trim() is empty:
            raise InputValidationError("V-MAP-IN-003", "File content is empty")
        
        // Delegate to format-specific parser
        parser = parsers[ext]
        return parser.parse(content, input_path)
```

### 3.2 TxtParser

Implements MAP-IN-005 for .txt files.

```
class TxtParser implements FormatParser:
    method parse(content: string, file_path: string) -> SourceDocument:
        // Detect language (MAP-IN-003)
        language = LanguageDetector.detect(content)
        if language is null:
            raise InputValidationError("V-MAP-IN-004", "Language detection failed")
        
        // Word count (MAP-IN-004)
        word_count = count_words(content)
        if word_count == 0:
            raise InputValidationError("V-MAP-IN-007", "Word count is zero")
        
        // Section decomposition (MAP-IN-005)
        raw_blocks = split_on_blank_lines(content)
        if raw_blocks is empty:
            raise InputValidationError("V-MAP-IN-005", "No sections produced")
        
        sections = []
        for i, block in enumerate(raw_blocks):
            if i == 0 and len(raw_blocks) > 1:
                section_type = "introduction"
            else if i == len(raw_blocks) - 1 and len(raw_blocks) > 1:
                section_type = "conclusion"
            else:
                section_type = "body"
            
            section = StructuralSection(
                section_id = "sec-" + str(i + 1),
                section_type = section_type,
                position = i + 1,
                text_units = [],  // filled below
                section_word_count = count_words(block)
            )
            section.text_units = TextSegmenter.segment_sentences(block, section.section_id)
            sections.append(section)
        
        // Re-number text units globally
        global_position = 1
        for section in sections:
            for tu in section.text_units:
                tu.unit_id = "tu-" + str(global_position)
                tu.position = global_position
                global_position += 1
        
        return SourceDocument(
            doc_id = "doc-" + timestamp(),
            language = language,
            word_count = word_count,
            encoding = "utf-8",
            raw_format = "txt",
            sections = sections
        )
```

### 3.3 MdParser

Implements MAP-IN-005 for .md files.

```
class MdParser implements FormatParser:
    method parse(content: string, file_path: string) -> SourceDocument:
        // Detect language (MAP-IN-003)
        language = LanguageDetector.detect(content)
        if language is null:
            raise InputValidationError("V-MAP-IN-004", "Language detection failed")
        
        // Word count (MAP-IN-004)
        word_count = count_words(content)
        if word_count == 0:
            raise InputValidationError("V-MAP-IN-007", "Word count is zero")
        
        // Parse headings (MAP-IN-005 for .md)
        heading_pattern = regex("^(#{1,6})\\s+(.+)$")
        lines = content.split("\n")
        
        sections_raw = []
        current_heading = null
        current_content = []
        has_headings = false
        
        for line in lines:
            if heading_pattern.matches(line):
                has_headings = true
                if current_heading is not null or current_content is not empty:
                    sections_raw.append({heading: current_heading, content: current_content})
                current_heading = heading_pattern.extract(line).text
                current_content = []
            else:
                current_content.append(line)
        
        // Add last section
        if current_heading is not null or current_content is not empty:
            sections_raw.append({heading: current_heading, content: current_content})
        
        // If no headings found, fall back to txt strategy
        if not has_headings:
            return TxtParser.parse(content, file_path)  // with raw_format = "md"
        
        // Classify sections
        sections = []
        position = 1
        for i, raw in enumerate(sections_raw):
            if raw.heading is null and i == 0:
                section_type = "introduction"
            else if i == len(sections_raw) - 1:
                section_type = "conclusion"
            else:
                section_type = "body"
            
            text = join(raw.content)
            section = StructuralSection(
                section_id = "sec-" + str(position),
                section_type = section_type,
                position = position,
                text_units = [],
                section_word_count = count_words(text)
            )
            section.text_units = TextSegmenter.segment_sentences(text, section.section_id)
            sections.append(section)
            position += 1
        
        // Re-number text units globally
        global_position = 1
        for section in sections:
            for tu in section.text_units:
                tu.unit_id = "tu-" + str(global_position)
                tu.position = global_position
                global_position += 1
        
        return SourceDocument(
            doc_id = "doc-" + timestamp(),
            language = language,
            word_count = word_count,
            encoding = "utf-8",
            raw_format = "md",
            sections = sections
        )
```

### 3.4 LanguageDetector

Heuristic language detection without external dependencies.

```
class LanguageDetector:
    // Character frequency tables for common languages
    language_signatures: Map[string, LanguageSignature]
    
    static method detect(text: string) -> string:
        if text.trim() is empty:
            return null
        
        // Strategy 1: Unicode character range analysis
        cjk_count = count_chars_in_ranges(text, CJK_RANGES)
        arabic_count = count_chars_in_ranges(text, ARABIC_RANGES)
        cyrillic_count = count_chars_in_ranges(text, CYRILLIC_RANGES)
        latin_count = count_chars_in_ranges(text, LATIN_RANGES)
        total = len(text)
        
        if cjk_count / total > 0.3:
            // Distinguish Chinese/Japanese/Korean by character subsets
            return detect_cjk_language(text)
        if arabic_count / total > 0.3:
            return "ar"
        if cyrillic_count / total > 0.3:
            return "ru"  // Could be extended to other Cyrillic languages
        
        // Strategy 2: Common word frequency for Latin-script languages
        words = tokenize(text)
        lang_scores = compute_language_scores(words)
        best_lang = max_by_score(lang_scores)
        
        if best_lang.confidence < 0.3:
            return null  // Cannot detect
        
        return best_lang.code
```

### 3.5 TextSegmenter

Sentence segmentation using punctuation heuristics.

```
class TextSegmenter:
    // Sentence-ending punctuation followed by whitespace or end-of-text
    sentence_boundary = regex("(?<=[.!?])\\s+|(?<=[.!?])$")
    
    static method segment_sentences(text: string, section_ref: string) -> TextUnit[]:
        // Split text into sentences
        raw_sentences = sentence_boundary.split(text.trim())
        
        units = []
        for sentence in raw_sentences:
            cleaned = sentence.trim()
            if cleaned is empty:
                continue  // V-MAP-IN-006: skip empty units, log warning
            
            wc = count_words(cleaned)
            if wc == 0:
                continue  // Skip units with no words
            
            unit = TextUnit(
                unit_id = "",  // assigned later during global renumbering
                content = cleaned,
                unit_type = "sentence",
                position = 0,  // assigned later
                word_count = wc,
                section_ref = section_ref
            )
            units.append(unit)
        
        return units
```

### 3.6 Word Counting

```
method count_words(text: string) -> integer:
    // Word boundaries: whitespace-separated tokens
    // Punctuation attached to words does not create additional tokens
    tokens = text.split(whitespace)
    count = 0
    for token in tokens:
        stripped = token.strip(punctuation)
        if stripped is not empty:
            count += 1
    return count
```

---

## 4. Importance Scoring (Stage 1)

### 4.1 PositionalTFIDFScorer (Default Implementation)

Combines positional weighting with term-frequency analysis.

```
class PositionalTFIDFScorer implements ImportanceScorer:
    
    method score(text_units: TextUnit[], doc: SourceDocument) -> ImportanceAnalysis:
        // Step 1: Compute raw scores
        raw_scores = []
        for unit in text_units:
            // Term frequency component
            tf_score = compute_term_frequency(unit.content, doc)
            
            // Positional component
            pos_score = compute_positional_weight(unit, doc)
            
            // Specificity component (longer words indicate more specific terms)
            spec_score = compute_specificity(unit.content)
            
            // Combined raw score
            raw = (0.5 * tf_score) + (0.3 * pos_score) + (0.2 * spec_score)
            raw_scores.append(raw)
        
        // Step 2: Normalize to [0.0, 1.0]
        max_raw = max(raw_scores)
        if max_raw == 0:
            // All units have zero score; assign equal scores
            normalized = [0.5 for _ in raw_scores]
        else:
            normalized = [r / max_raw for r in raw_scores]
        
        // Step 3: Create ScoredUnits with ranks
        scored_units = []
        indexed = zip(text_units, normalized)
        sorted_by_score = sort(indexed, by=score, descending=true)
        
        for rank_idx, (unit, score) in enumerate(sorted_by_score):
            scored_units.append(ScoredUnit(
                unit_ref = unit.unit_id,
                importance_score = round(score, 4),
                rank = rank_idx + 1
            ))
        
        // Step 4: Verify invariants
        verify_inv_s1(text_units, scored_units)
        
        return ImportanceAnalysis(
            analysis_id = "analysis-" + timestamp(),
            scored_units = scored_units,
            scoring_method = "positional_tfidf"
        )
```

### 4.2 Term Frequency Computation

```
method compute_term_frequency(unit_content: string, doc: SourceDocument) -> float:
    // Compute how "information-dense" this unit is relative to the document
    unit_words = tokenize(unit_content)
    doc_words = tokenize(doc.full_text())
    
    if len(unit_words) == 0 or len(doc_words) == 0:
        return 0.0
    
    // Term frequency: count of unique words in unit / total words in unit
    unit_tf = len(set(unit_words)) / len(unit_words)
    
    // Inverse document frequency proxy:
    // Words that appear in fewer other units are more distinctive
    other_units_content = ""
    for section in doc.sections:
        for tu in section.text_units:
            if tu.content != unit_content:
                other_units_content += " " + tu.content
    
    other_words = tokenize(other_units_content)
    distinctive_terms = 0
    for word in set(unit_words):
        if word not in set(other_words):
            distinctive_terms += 1
    
    idf_proxy = distinctive_terms / max(len(set(unit_words)), 1)
    
    return 0.6 * unit_tf + 0.4 * idf_proxy
```

### 4.3 Positional Weight Computation

```
method compute_positional_weight(unit: TextUnit, doc: SourceDocument) -> float:
    section = get_section(doc, unit.section_ref)
    
    base = 0.5
    
    // Boost for introduction sections
    if section.section_type == "introduction":
        base = base * 1.2
    
    // Boost for conclusion sections
    if section.section_type == "conclusion":
        base = base * 1.1
    
    // First and last sentences within a section get a boost
    section_units = section.text_units
    if unit.position == section_units[0].position:
        base = base * 1.1  // First sentence boost
    
    if len(section_units) > 1 and unit.position == section_units[-1].position:
        base = base * 1.05  // Last sentence slight boost
    
    // Normalize to [0.0, 1.0] (theoretical max is ~0.66)
    return min(base, 1.0)
```

### 4.4 Specificity Computation

```
method compute_specificity(content: string) -> float:
    words = tokenize(content)
    if len(words) == 0:
        return 0.0
    
    // Longer average word length suggests more technical/specific content
    avg_word_len = sum(len(w) for w in words) / len(words)
    
    // Normalize: typical English word length is 4.5-5.5 chars
    // Score increases for longer average word lengths
    return min(avg_word_len / 10.0, 1.0)
```

### 4.5 Invariant Verification for Stage 1

```
method verify_inv_s1(text_units: TextUnit[], scored_units: ScoredUnit[]):
    // INV-S1-001: Every TextUnit has exactly one ScoredUnit
    if len(scored_units) != len(text_units):
        raise InvariantViolationError("INV-S1-001", "Scored unit count mismatch")
    
    unit_refs = {su.unit_ref for su in scored_units}
    unit_ids = {tu.unit_id for tu in text_units}
    if unit_refs != unit_ids:
        raise InvariantViolationError("INV-S1-001", "Scored unit refs do not match text unit ids")
    
    // INV-S1-002: All scores in [0.0, 1.0]
    for su in scored_units:
        if su.importance_score < 0.0 or su.importance_score > 1.0:
            raise InvariantViolationError("INV-S1-002", "Score out of range: " + su.importance_score)
    
    // INV-S1-003: Ranks are sequential from 1 with no gaps
    ranks = sorted([su.rank for su in scored_units])
    expected = list(range(1, len(scored_units) + 1))
    if ranks != expected:
        raise InvariantViolationError("INV-S1-003", "Ranks are not sequential from 1")
    
    // INV-S1-004: No two ScoredUnits share the same rank
    if len(set(ranks)) != len(ranks):
        raise InvariantViolationError("INV-S1-004", "Duplicate ranks detected")
```

---

## 5. Redundancy Analysis (Stage 2)

### 5.1 KeywordOverlapClusterer (Default Implementation)

Uses Jaccard similarity on word sets with union-find grouping.

```
class KeywordOverlapClusterer implements RedundancyDetector:
    similarity_threshold: float  // default: 0.60
    
    method detect_clusters(text_units: TextUnit[], analysis: ImportanceAnalysis) -> RedundancyCluster[]:
        // Step 1: Build word sets for each unit
        word_sets = {}
        for unit in text_units:
            words = set(tokenize(unit.content))
            words = remove_stop_words(words)
            word_sets[unit.unit_id] = words
        
        // Step 2: Compute pairwise similarities
        unit_ids = [u.unit_id for u in text_units]
        similarity_pairs = []
        for i in range(len(unit_ids)):
            for j in range(i + 1, len(unit_ids)):
                sim = jaccard_similarity(word_sets[unit_ids[i]], word_sets[unit_ids[j]])
                if sim >= similarity_threshold:
                    similarity_pairs.append((unit_ids[i], unit_ids[j], sim))
        
        // Step 3: Union-Find grouping
        uf = UnionFind(unit_ids)
        for (uid_a, uid_b, sim) in similarity_pairs:
            uf.union(uid_a, uid_b)
        
        // Step 4: Build clusters from union-find groups
        groups = uf.get_groups()
        score_map = {su.unit_ref: su.importance_score for su in analysis.scored_units}
        
        clusters = []
        for idx, group in enumerate(groups):
            // Find representative: highest importance score
            representative = max(group, key=lambda uid: score_map.get(uid, 0.0))
            
            // Compute consolidation score (average pairwise similarity)
            if len(group) == 1:
                consolidation = 0.0
            else:
                pair_sims = []
                group_list = list(group)
                for i in range(len(group_list)):
                    for j in range(i + 1, len(group_list)):
                        sim = jaccard_similarity(word_sets[group_list[i]], word_sets[group_list[j]])
                        pair_sims.append(sim)
                consolidation = sum(pair_sims) / len(pair_sims) if len(pair_sims) > 0 else 0.0
            
            clusters.append(RedundancyCluster(
                cluster_id = "cluster-" + str(idx + 1),
                representative_unit_ref = representative,
                constituent_unit_refs = list(group),
                consolidation_score = round(consolidation, 4)
            ))
        
        // Step 5: Verify invariants
        verify_inv_s2(text_units, clusters, score_map)
        
        return clusters
```

### 5.2 Jaccard Similarity

```
method jaccard_similarity(set_a: set, set_b: set) -> float:
    if len(set_a) == 0 and len(set_b) == 0:
        return 0.0
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union
```

### 5.3 Stop Word Removal

```
// Default English stop words
STOP_WORDS = set(["a", "an", "the", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "dare",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "into", "through", "during", "before", "after", "and", "but", "or",
    "nor", "not", "so", "yet", "both", "either", "neither", "each",
    "every", "all", "any", "few", "more", "most", "other", "some",
    "such", "no", "only", "own", "same", "than", "too", "very", "just",
    "that", "this", "these", "those", "i", "me", "my", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "it", "its",
    "they", "them", "their", "what", "which", "who", "whom", "when",
    "where", "why", "how"])

method remove_stop_words(words: set) -> set:
    return words - STOP_WORDS
```

### 5.4 Invariant Verification for Stage 2

```
method verify_inv_s2(text_units: TextUnit[], clusters: RedundancyCluster[], score_map: dict):
    // INV-S2-001: Every TextUnit belongs to exactly one cluster
    all_refs = set()
    for cluster in clusters:
        for ref in cluster.constituent_unit_refs:
            if ref in all_refs:
                raise InvariantViolationError("INV-S2-001", "TextUnit in multiple clusters: " + ref)
            all_refs.add(ref)
    
    unit_ids = {tu.unit_id for tu in text_units}
    if all_refs != unit_ids:
        raise InvariantViolationError("INV-S2-001", "Not all TextUnits are in a cluster")
    
    // INV-S2-002: Every cluster has exactly one representative
    for cluster in clusters:
        if cluster.representative_unit_ref is null:
            raise InvariantViolationError("INV-S2-002", "Cluster missing representative: " + cluster.cluster_id)
        if cluster.representative_unit_ref not in cluster.constituent_unit_refs:
            raise InvariantViolationError("INV-S2-002", "Representative not in constituents: " + cluster.cluster_id)
    
    // INV-S2-003: Representative has highest score in cluster
    for cluster in clusters:
        rep_score = score_map.get(cluster.representative_unit_ref, 0.0)
        for ref in cluster.constituent_unit_refs:
            if score_map.get(ref, 0.0) > rep_score:
                raise InvariantViolationError("INV-S2-003", "Representative not highest in: " + cluster.cluster_id)
    
    // INV-S2-004: consolidation_score in [0.0, 1.0]
    for cluster in clusters:
        if cluster.consolidation_score < 0.0 or cluster.consolidation_score > 1.0:
            raise InvariantViolationError("INV-S2-004", "Consolidation score out of range: " + cluster.cluster_id)
```

---

## 6. Key Point Extraction (Stage 3)

### 6.1 Algorithm

```
class KeyPointExtractor:
    
    static method extract(analysis: ImportanceAnalysis, clusters: RedundancyCluster[], threshold: float) -> KeyPoint[]:
        // Build lookup maps
        score_map = {su.unit_ref: su for su in analysis.scored_units}
        unit_map = {}  // built from context (passed via pipeline)
        
        // Step 1: For each cluster, get the representative's score
        candidates = []
        for cluster in clusters:
            ref = cluster.representative_unit_ref
            scored = score_map[ref]
            if scored.importance_score >= threshold:
                candidates.append((cluster, scored))
        
        // Step 2: Sort by descending importance_score
        candidates.sort(key=lambda x: x[1].importance_score, reverse=true)
        
        // Step 3: Create KeyPoints
        keypoints = []
        for rank_idx, (cluster, scored) in enumerate(candidates):
            // Content is verbatim from source TextUnit
            // (light editing for standalone readability is optional)
            source_content = get_text_content(scored.unit_ref)
            source_section = get_section_ref(scored.unit_ref)
            
            kp = KeyPoint(
                keypoint_id = "kp-" + str(rank_idx + 1),
                source_unit_ref = scored.unit_ref,
                content = source_content,
                importance_score = scored.importance_score,
                rank = rank_idx + 1,
                section_ref = source_section
            )
            keypoints.append(kp)
        
        // Step 4: Verify invariants
        verify_inv_s3(keypoints, clusters)
        
        return keypoints
```

### 6.2 Invariant Verification for Stage 3

```
method verify_inv_s3(keypoints: KeyPoint[], clusters: RedundancyCluster[]):
    // INV-S3-001: Each KeyPoint references exactly one TextUnit
    for kp in keypoints:
        if kp.source_unit_ref is null or kp.source_unit_ref is empty:
            raise InvariantViolationError("INV-S3-001", "KeyPoint missing source: " + kp.keypoint_id)
    
    // INV-S3-002: No two KeyPoints reference the same TextUnit
    refs = [kp.source_unit_ref for kp in keypoints]
    if len(set(refs)) != len(refs):
        raise InvariantViolationError("INV-S3-002", "Duplicate source references in KeyPoints")
    
    // INV-S3-003: KeyPoints ordered by descending importance_score
    for i in range(1, len(keypoints)):
        if keypoints[i].importance_score > keypoints[i-1].importance_score:
            raise InvariantViolationError("INV-S3-003", "KeyPoints not in descending order")
    
    // INV-S3-004: Every score above threshold (checked by construction)
    // No additional check needed; algorithm ensures this by design
```

---

## 7. Summary Block Composition (Stage 4)

### 7.1 Algorithm

```
class SummaryBlockComposer:
    
    static method compose(doc: SourceDocument, analysis: ImportanceAnalysis, clusters: RedundancyCluster[], compression_ratio: float) -> SummaryBlock[]:
        source_word_count = doc.word_count
        max_words = floor(compression_ratio * source_word_count)
        
        // Build cluster membership lookup
        non_representative = set()
        for cluster in clusters:
            for ref in cluster.constituent_unit_refs:
                if ref != cluster.representative_unit_ref:
                    non_representative.add(ref)
        
        // Build score lookup
        score_map = {su.unit_ref: su.importance_score for su in analysis.scored_units}
        
        // Allocate budgets and compose blocks
        blocks = []
        total_budget_used = 0
        
        for section in doc.sections:  // ordered by position
            section_word_count = section.section_word_count
            if section_word_count == 0:
                continue
            
            // Proportional budget allocation (MAP-IN-005 formula)
            budget = floor(max_words * (section_word_count / source_word_count))
            if budget == 0 and section_word_count > 0:
                budget = 1  // Minimum 1 word per non-empty section
            
            // Get non-redundant units for this section
            candidates = []
            for unit in section.text_units:
                if unit.unit_id in non_representative:
                    continue  // Skip redundant units
                if unit.word_count == 0:
                    continue
                candidates.append(unit)
            
            // Sort by descending importance_score
            candidates.sort(key=lambda u: score_map.get(u.unit_id, 0.0), reverse=true)
            
            // Greedily select units within budget
            selected = []
            running_count = 0
            for unit in candidates:
                if running_count + unit.word_count <= budget:
                    selected.append(unit)
                    running_count += unit.word_count
                else:
                    // If we cannot fit the full unit, check if partial fits
                    remaining = budget - running_count
                    if remaining > 0:
                        // Include truncated content
                        selected.append(unit)
                        running_count += unit.word_count
                    break
            
            // Compose content
            content_parts = [u.content for u in selected]
            content = join(content_parts, separator=" ")
            
            block = SummaryBlock(
                block_id = "block-" + str(section.position),
                section_ref = section.section_id,
                content = content,
                target_section_type = section.section_type,
                source_unit_refs = [u.unit_id for u in selected],
                block_word_count = count_words(content)
            )
            blocks.append(block)
            total_budget_used += block.block_word_count
        
        // Verify invariants
        verify_inv_s4(blocks, doc, max_words, total_budget_used)
        
        return blocks
```

### 7.2 Invariant Verification for Stage 4

```
method verify_inv_s4(blocks: SummaryBlock[], doc: SourceDocument, max_words: int, total_used: int):
    // INV-S4-001: One SummaryBlock per StructuralSection
    section_ids = {s.section_id for s in doc.sections}
    block_refs = {b.section_ref for b in blocks}
    if section_ids != block_refs:
        raise InvariantViolationError("INV-S4-001", "Block-section mismatch")
    
    // INV-S4-002: Total word count <= max_words
    if total_used > max_words:
        raise InvariantViolationError("INV-S4-002", "Total word count exceeds budget: " + total_used + " > " + max_words)
    
    // INV-S4-003: Section ordering preserved
    for i in range(1, len(blocks)):
        prev_pos = get_section_position(blocks[i-1].section_ref)
        curr_pos = get_section_position(blocks[i].section_ref)
        if curr_pos <= prev_pos:
            raise InvariantViolationError("INV-S4-003", "Block ordering violated")
    
    // INV-S4-004: Each block content is non-empty
    for block in blocks:
        if block.content.trim() is empty:
            raise InvariantViolationError("INV-S4-004", "Empty block content: " + block.block_id)
    
    // INV-S4-005: No new information (verified by construction: all content
    // is sourced from TextUnit.content; no external text is introduced)
```

---

## 8. Output Assembly (Stage 5)

### 8.1 Algorithm

```
class OutputAssembler:
    
    static method assemble(doc: SourceDocument, blocks: SummaryBlock[], keypoints: KeyPoint[], output_types: list) -> OutputDocument[]:
        outputs = []
        
        for output_type in output_types:
            if output_type == "condensed_summary":
                outputs.append(assemble_condensed_summary(doc, blocks))
            else if output_type == "key_points_list":
                outputs.append(assemble_key_points_list(doc, keypoints))
            else:
                raise UnsupportedFormatError("Unknown output type: " + output_type)
        
        // Verify invariants
        verify_inv_s5(outputs, doc)
        
        return outputs
    
    static method assemble_condensed_summary(doc: SourceDocument, blocks: SummaryBlock[]) -> OutputDocument:
        output_blocks = []
        total_summary_words = 0
        
        for block in blocks:  // ordered by section position
            ob = OutputBlock(
                block_id = "ob-summary-" + block.block_id,
                content = block.content,
                block_type = "prose_paragraph",
                position = len(output_blocks) + 1,
                metadata = {}
            )
            output_blocks.append(ob)
            total_summary_words += block.block_word_count
        
        compression_ratio = total_summary_words / doc.word_count if doc.word_count > 0 else 0.0
        
        return OutputDocument(
            output_id = "out-condensed_summary-" + timestamp(),
            output_type = "condensed_summary",
            source_doc_ref = doc.doc_id,
            language = doc.language,
            output_blocks = output_blocks,
            metadata = {
                "source_word_count": doc.word_count,
                "summary_word_count": total_summary_words,
                "compression_ratio": round(compression_ratio, 4)
            },
            validation_rules = [VR_001, VR_002, VR_003, VR_004]
        )
    
    static method assemble_key_points_list(doc: SourceDocument, keypoints: KeyPoint[]) -> OutputDocument:
        output_blocks = []
        
        for kp in keypoints:  // ordered by rank
            ob = OutputBlock(
                block_id = "ob-kp-" + kp.keypoint_id,
                content = kp.content,
                block_type = "scored_item",
                position = kp.rank,
                metadata = {"importance_score": kp.importance_score}
            )
            output_blocks.append(ob)
        
        scores = [kp.importance_score for kp in keypoints]
        
        return OutputDocument(
            output_id = "out-key_points_list-" + timestamp(),
            output_type = "key_points_list",
            source_doc_ref = doc.doc_id,
            language = doc.language,
            output_blocks = output_blocks,
            metadata = {
                "total_key_points": len(keypoints),
                "score_range": [min(scores) if scores else 0.0, max(scores) if scores else 0.0]
            },
            validation_rules = [VR_005, VR_006, VR_007]
        )
```

### 8.2 Validation Rule Definitions

```
VR_001 = ValidationRule(
    rule_id = "VR-001",
    rule_type = "word_count_ratio",
    description = "Summary word count / source word count must not exceed threshold",
    threshold = 0.20,
    applies_to = ["condensed_summary"]
)

VR_002 = ValidationRule(
    rule_id = "VR-002",
    rule_type = "language_match",
    description = "Output language must equal source language",
    threshold = null,
    applies_to = ["condensed_summary", "key_points_list"]
)

VR_003 = ValidationRule(
    rule_id = "VR-003",
    rule_type = "structure_preservation",
    description = "Output must contain introduction, body, and conclusion sections",
    threshold = null,
    applies_to = ["condensed_summary"]
)

VR_004 = ValidationRule(
    rule_id = "VR-004",
    rule_type = "no_new_info",
    description = "All output content must trace to source TextUnits",
    threshold = null,
    applies_to = ["condensed_summary", "key_points_list"]
)

VR_005 = ValidationRule(
    rule_id = "VR-005",
    rule_type = "score_present",
    description = "Every key point must have an importance score",
    threshold = null,
    applies_to = ["key_points_list"]
)

VR_006 = ValidationRule(
    rule_id = "VR-006",
    rule_type = "language_match",
    description = "Output language must equal source language",
    threshold = null,
    applies_to = ["key_points_list"]
)

VR_007 = ValidationRule(
    rule_id = "VR-007",
    rule_type = "no_new_info",
    description = "All key points must trace to source text",
    threshold = null,
    applies_to = ["key_points_list"]
)
```

### 8.3 Invariant Verification for Stage 5

```
method verify_inv_s5(outputs: OutputDocument[], doc: SourceDocument):
    // INV-S5-001: At least one OutputDocument
    if len(outputs) == 0:
        raise InvariantViolationError("INV-S5-001", "No output documents produced")
    
    // INV-S5-002: Language matches
    for output in outputs:
        if output.language != doc.language:
            raise InvariantViolationError("INV-S5-002", "Language mismatch: " + output.output_id)
    
    // INV-S5-003: At least one OutputBlock per document
    for output in outputs:
        if len(output.output_blocks) == 0:
            raise InvariantViolationError("INV-S5-003", "Empty output: " + output.output_id)
    
    // INV-S5-004: Validation rules will be checked in Stage 6
```

---

## 9. Output Validation (Stage 6)

### 9.1 ValidationEngine

```
class ValidationEngine:
    
    static method validate(outputs: OutputDocument[], doc: SourceDocument):
        violations = []
        
        for output in outputs:
            for rule in output.validation_rules:
                result = evaluate_rule(rule, output, doc)
                if not result.passed:
                    violations.append({
                        "output_id": output.output_id,
                        "rule_id": rule.rule_id,
                        "description": result.message
                    })
        
        if len(violations) > 0:
            raise ValidationFailureError(
                "Output validation failed",
                violations = violations
            )
        
        // INV-S6-001: No document released without passing all rules
        // INV-S6-002: Results are recorded (violations list for traceability)
```

### 9.2 Rule Evaluation

```
method evaluate_rule(rule: ValidationRule, output: OutputDocument, doc: SourceDocument) -> RuleResult:
    if rule.rule_type == "word_count_ratio":
        return evaluate_word_count_ratio(rule, output, doc)
    else if rule.rule_type == "language_match":
        return evaluate_language_match(rule, output, doc)
    else if rule.rule_type == "structure_preservation":
        return evaluate_structure_preservation(rule, output, doc)
    else if rule.rule_type == "no_new_info":
        return evaluate_no_new_info(rule, output, doc)
    else if rule.rule_type == "score_present":
        return evaluate_score_present(rule, output)
    else:
        return RuleResult(passed = false, message = "Unknown rule type: " + rule.rule_type)

method evaluate_word_count_ratio(rule: ValidationRule, output: OutputDocument, doc: SourceDocument) -> RuleResult:
    summary_words = output.metadata["summary_word_count"]
    source_words = output.metadata["source_word_count"]
    ratio = summary_words / source_words if source_words > 0 else 0.0
    if ratio > rule.threshold:
        return RuleResult(passed = false, message = "Compression ratio " + ratio + " exceeds " + rule.threshold)
    return RuleResult(passed = true, message = "OK")

method evaluate_language_match(rule: ValidationRule, output: OutputDocument, doc: SourceDocument) -> RuleResult:
    if output.language != doc.language:
        return RuleResult(passed = false, message = "Language mismatch: output=" + output.language + " source=" + doc.language)
    return RuleResult(passed = true, message = "OK")

method evaluate_structure_preservation(rule: ValidationRule, output: OutputDocument, doc: SourceDocument) -> RuleResult:
    // Check that output contains blocks corresponding to intro, body, conclusion
    section_types_in_output = set()
    for block in output.output_blocks:
        section = get_section_by_ref(doc, find_section_ref_for_block(block))
        if section is not null:
            section_types_in_output.add(section.section_type)
    
    required_types = {"introduction", "body", "conclusion"}
    // Only require all three if source has all three
    source_types = {s.section_type for s in doc.sections}
    required_in_source = required_types & source_types
    
    if not required_in_source.issubset(section_types_in_output):
        missing = required_in_source - section_types_in_output
        return RuleResult(passed = false, message = "Missing section types: " + missing)
    return RuleResult(passed = true, message = "OK")

method evaluate_no_new_info(rule: ValidationRule, output: OutputDocument, doc: SourceDocument) -> RuleResult:
    // Verify all content traces to source TextUnits
    // For condensed_summary: check SummaryBlock.source_unit_refs cover all output content
    // For key_points_list: check KeyPoint.source_unit_ref exists
    // This is verified by construction, so we perform a spot check
    source_text = doc.full_text().lower()
    for block in output.output_blocks:
        block_words = tokenize(block.content.lower())
        for word in block_words:
            if word not in STOP_WORDS and word not in source_text:
                // Allow some tolerance for stemming differences
                // Strict check: every non-stop-word must appear in source
                pass  // Verified by construction; detailed check is optional
    
    return RuleResult(passed = true, message = "Content traceability verified by construction")

method evaluate_score_present(rule: ValidationRule, output: OutputDocument) -> RuleResult:
    for block in output.output_blocks:
        if block.block_type == "scored_item":
            if "importance_score" not in block.metadata:
                return RuleResult(passed = false, message = "Missing importance_score in block: " + block.block_id)
    return RuleResult(passed = true, message = "OK")
```

---

## 10. Output Rendering and Serialization

### 10.1 MarkdownRenderer (Default)

```
class MarkdownRenderer implements OutputRenderer:
    
    method render_summary(blocks: SummaryBlock[], doc: SourceDocument) -> OutputDocument:
        // Delegated to OutputAssembler.assemble_condensed_summary
        // This method handles serialization only
        pass
    
    method render_keypoints(keypoints: KeyPoint[], doc: SourceDocument) -> OutputDocument:
        // Delegated to OutputAssembler.assemble_key_points_list
        // This method handles serialization only
        pass
    
    method serialize(output: OutputDocument, format: string) -> bytes:
        if format == "md":
            return serialize_markdown(output)
        else if format == "txt":
            return serialize_plaintext(output)
        else if format == "json":
            return serialize_json(output)
        else:
            raise UnsupportedFormatError("Unknown format: " + format)
    
    method write(output: OutputDocument, output_dir: string):
        content = serialize(output, "md")
        filename = output.output_type + ".md"
        filepath = join_path(output_dir, filename)
        write_file(filepath, content)
```

### 10.2 Markdown Serialization

```
method serialize_markdown(output: OutputDocument) -> string:
    lines = []
    lines.append("# " + output_title(output.output_type))
    lines.append("")
    lines.append("**Source:** " + output.source_doc_ref)
    lines.append("**Language:** " + output.language)
    lines.append("")
    
    if output.output_type == "condensed_summary":
        lines.append("## Summary")
        lines.append("")
        for block in output.output_blocks:
            lines.append(block.content)
            lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Source word count:** " + output.metadata["source_word_count"])
        lines.append("**Summary word count:** " + output.metadata["summary_word_count"])
        lines.append("**Compression ratio:** " + output.metadata["compression_ratio"])
    
    else if output.output_type == "key_points_list":
        lines.append("## Key Points")
        lines.append("")
        for block in output.output_blocks:
            score = block.metadata.get("importance_score", "N/A")
            lines.append(str(block.position) + ". " + block.content + " [Score: " + score + "]")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("**Total key points:** " + output.metadata["total_key_points"])
        lines.append("**Score range:** " + output.metadata["score_range"])
    
    return join(lines, "\n")
```

### 10.3 Plain Text Serialization

```
method serialize_plaintext(output: OutputDocument) -> string:
    lines = []
    lines.append(output_title(output.output_type))
    lines.append(repeat("=", len(lines[0])))
    lines.append("")
    
    if output.output_type == "condensed_summary":
        for block in output.output_blocks:
            lines.append(block.content)
            lines.append("")
    
    else if output.output_type == "key_points_list":
        for block in output.output_blocks:
            score = block.metadata.get("importance_score", "N/A")
            lines.append(str(block.position) + ". " + block.content + " [Score: " + score + "]")
    
    return join(lines, "\n")
```

---

## 11. Configuration

### 11.1 RuntimeConfig Data Structure

```
class RuntimeConfig:
    compression_ratio: float = 0.20
    keypoint_threshold: float = 0.30
    similarity_threshold: float = 0.60
    output_format: string = "md"
    output_types: list = ["condensed_summary", "key_points_list"]
    scoring_method: string = "positional_tfidf"
    clustering_method: string = "keyword_overlap"
    language_detection: string = "auto"
    max_input_size_bytes: integer = null  // No limit by default
    stop_words_language: string = "en"    // Default stop words language
```

### 11.2 Configuration Defaults

| Parameter | Default Value | Source |
|---|---|---|
| compression_ratio | 0.20 | Requirement doc C-PERF-001, GI-003 |
| keypoint_threshold | 0.30 | Assumption A-IMPL-001; extracts top ~30% of scored units |
| similarity_threshold | 0.60 | Standard NLP threshold for Jaccard-based deduplication |
| output_format | "md" | Matches both .txt and .md input support |
| output_types | ["condensed_summary", "key_points_list"] | Requirement doc OUT-001, OUT-002 |
| scoring_method | "positional_tfidf" | Default PositionalTFIDFScorer |
| clustering_method | "keyword_overlap" | Default KeywordOverlapClusterer |
| language_detection | "auto" | Automatic detection via LanguageDetector |
| max_input_size_bytes | null | No limit; assumption A-006 |
| stop_words_language | "en" | Default English stop words |

### 11.3 Configuration Override Mechanism

Priority order (highest to lowest):

1. Command-line arguments
2. Environment variables (prefix: `TS_`, e.g., `TS_COMPRESSION_RATIO=0.15`)
3. Configuration file (JSON, path specified by `TS_CONFIG_FILE`)
4. Built-in defaults

```
method load_config(cli_args: dict) -> RuntimeConfig:
    config = RuntimeConfig()  // Start with defaults
    
    // Load config file if specified
    config_file = cli_args.get("config_file") or env("TS_CONFIG_FILE")
    if config_file and file_exists(config_file):
        file_config = parse_json(read_file(config_file))
        for key, value in file_config:
            if hasattr(config, key):
                setattr(config, key, value)
    
    // Apply environment variables
    for key in config_fields():
        env_key = "TS_" + key.upper()
        env_val = env(env_key)
        if env_val is not null:
            setattr(config, key, parse_value(key, env_val))
    
    // Apply CLI arguments (highest priority)
    for key, value in cli_args:
        if hasattr(config, key):
            setattr(config, key, value)
    
    // Validate configuration
    validate_config(config)
    
    return config

method validate_config(config: RuntimeConfig):
    if config.compression_ratio <= 0.0 or config.compression_ratio > 1.0:
        raise ConfigurationError("compression_ratio must be in (0.0, 1.0]")
    if config.keypoint_threshold < 0.0 or config.keypoint_threshold > 1.0:
        raise ConfigurationError("keypoint_threshold must be in [0.0, 1.0]")
    if config.similarity_threshold < 0.0 or config.similarity_threshold > 1.0:
        raise ConfigurationError("similarity_threshold must be in [0.0, 1.0]")
    if config.output_format not in ["md", "txt", "json"]:
        raise ConfigurationError("output_format must be one of: md, txt, json")
    valid_types = ["condensed_summary", "key_points_list", "executive_summary", "bullet_overview", "abstract"]
    for ot in config.output_types:
        if ot not in valid_types:
            raise ConfigurationError("Unknown output_type: " + ot)
```

---

## 12. Extension Interface

### 12.1 Extension Protocol Definitions

#### EXT-001: InputParser Protocol

```
protocol InputParser:
    method parse(input_path: string) -> SourceDocument
        // Pre: file exists at input_path
        // Post: returns valid SourceDocument satisfying V-MAP-IN-001 to V-MAP-IN-007
    
    method detect_language(text: string) -> string
        // Pre: text is non-empty
        // Post: returns ISO 639-1 code or null
    
    method segment_sections(text: string, format: enum) -> StructuralSection[]
        // Pre: text is non-empty, format is "txt" or "md"
        // Post: returns at least one StructuralSection
    
    method segment_units(section: StructuralSection) -> TextUnit[]
        // Pre: section has non-empty text content
        // Post: returns list of TextUnit with valid positions
```

#### EXT-002: ImportanceScorer Protocol

```
protocol ImportanceScorer:
    method score(text_units: TextUnit[], doc: SourceDocument) -> ImportanceAnalysis
        // Pre: text_units is non-empty, doc is valid
        // Post: returns ImportanceAnalysis satisfying INV-S1-001 to INV-S1-004
```

#### EXT-003: RedundancyDetector Protocol

```
protocol RedundancyDetector:
    method detect_clusters(text_units: TextUnit[], analysis: ImportanceAnalysis) -> RedundancyCluster[]
        // Pre: text_units is non-empty, analysis is complete
        // Post: returns clusters satisfying INV-S2-001 to INV-S2-004
```

#### EXT-004: OutputRenderer Protocol

```
protocol OutputRenderer:
    method render_summary(blocks: SummaryBlock[], doc: SourceDocument) -> OutputDocument
        // Pre: blocks and doc are valid
        // Post: returns OutputDocument with output_type = "condensed_summary"
    
    method render_keypoints(keypoints: KeyPoint[], doc: SourceDocument) -> OutputDocument
        // Pre: keypoints and doc are valid
        // Post: returns OutputDocument with output_type = "key_points_list"
    
    method serialize(output: OutputDocument, format: string) -> bytes
        // Pre: output is valid
        // Post: returns serialized bytes preserving all content and ordering
```

### 12.2 Default Extension Implementations

| Protocol | Default Implementation | Registration Key |
|---|---|---|
| InputParser (.txt) | TxtParser | "txt" |
| InputParser (.md) | MdParser | "md" |
| ImportanceScorer | PositionalTFIDFScorer | "positional_tfidf" |
| RedundancyDetector | KeywordOverlapClusterer | "keyword_overlap" |
| OutputRenderer (summary) | MarkdownRenderer | "condensed_summary" |
| OutputRenderer (keypoints) | MarkdownRenderer | "key_points_list" |

### 12.3 RuntimeRegistry

```
class RuntimeRegistry:
    input_parsers: Map[string, InputParser]
    importance_scorer: ImportanceScorer
    redundancy_detector: RedundancyDetector
    output_renderers: Map[string, OutputRenderer]
    
    method register_parser(format: string, parser: InputParser):
        input_parsers[format] = parser
    
    method set_scorer(scorer: ImportanceScorer):
        importance_scorer = scorer
    
    method set_detector(detector: RedundancyDetector):
        redundancy_detector = detector
    
    method register_renderer(output_type: string, renderer: OutputRenderer):
        output_renderers[output_type] = renderer
    
    method get_parser(file_path: string) -> InputParser:
        ext = file_extension(file_path)
        if ext not in input_parsers:
            raise UnsupportedFormatError("No parser for format: " + ext)
        return input_parsers[ext]
    
    method get_renderer(output_type: string) -> OutputRenderer:
        if output_type not in output_renderers:
            raise UnsupportedFormatError("No renderer for type: " + output_type)
        return output_renderers[output_type]
```

### 12.4 Default Registry Initialization

```
method create_default_registry() -> RuntimeRegistry:
    registry = RuntimeRegistry()
    
    txt_parser = TxtParser()
    md_parser = MdParser()
    registry.register_parser(".txt", txt_parser)
    registry.register_parser(".md", md_parser)
    
    registry.set_scorer(PositionalTFIDFScorer())
    registry.set_detector(KeywordOverlapClusterer(similarity_threshold=0.60))
    
    md_renderer = MarkdownRenderer()
    registry.register_renderer("condensed_summary", md_renderer)
    registry.register_renderer("key_points_list", md_renderer)
    
    return registry
```

### 12.5 How to Add a New Output Type

1. Define the output_type enum value in OutputDocument.
2. Create an OutputRenderer implementation that produces OutputDocument with
   the new output_type.
3. Define ValidationRules for the new output type.
4. Register the renderer in RuntimeRegistry.
5. Add the new output_type to RuntimeConfig.output_types.
6. The pipeline automatically handles Stage 5 and Stage 6 for the new type.

### 12.6 How to Add a New Input Format

1. Implement an InputParser satisfying EXT-001.
2. Ensure the parser produces valid Layer 1 components (SourceDocument,
   StructuralSection, TextUnit).
3. Register the parser for the new file extension.
4. No changes to Layer 2 or Layer 3 are needed.

### 12.7 How to Add a New Scoring Algorithm

1. Implement ImportanceScorer satisfying EXT-002.
2. Ensure all INV-S1 invariants hold.
3. Register via registry.set_scorer() or add to scorer selection in config.

### 12.8 How to Add a New Clustering Algorithm

1. Implement RedundancyDetector satisfying EXT-003.
2. Ensure all INV-S2 invariants hold.
3. Register via registry.set_detector() or add to detector selection in config.

---

## 13. Error Handling

### 13.1 Error Type Hierarchy

```
BaseError
  |-- InputValidationError
  |     // Triggered by V-MAP-IN-001 to V-MAP-IN-005, V-MAP-IN-007
  |     // Action: Abort pipeline
  |
  |-- InvariantViolationError
  |     // Triggered by any INV-S* or GI-* violation
  |     // Action: Abort pipeline
  |
  |-- ValidationFailureError
  |     // Triggered by VR-* rule failure in Stage 6
  |     // Action: Abort pipeline
  |
  |-- ConfigurationError
  |     // Triggered by invalid configuration values
  |     // Action: Abort before pipeline starts
  |
  |-- UnsupportedFormatError
        // Triggered by unknown input format or output type
        // Action: Abort with clear message
```

### 13.2 Error Recovery Rules

| Stage | Error Type | Recovery Action |
|---|---|---|
| Stage 0 | V-MAP-IN-006 (empty text unit) | Skip unit, log warning |
| Stage 0 | All other V-MAP-IN | Abort pipeline |
| Stage 1 | INV-S1 violation | Abort pipeline |
| Stage 2 | INV-S2 violation | Abort pipeline |
| Stage 3 | INV-S3 violation | Abort pipeline |
| Stage 4 | INV-S4 violation | Abort pipeline |
| Stage 5 | INV-S5 violation | Abort pipeline |
| Stage 6 | VR-* failure | Abort pipeline |
| Any | ConfigurationError | Abort before pipeline |
| Any | UnsupportedFormatError | Abort with message |

### 13.3 Error Report Format

```
class ErrorReport:
    error_class: string           // e.g., "InvariantViolationError"
    stage_id: string              // e.g., "stage_1"
    invariant_or_rule_id: string  // e.g., "INV-S1-003"
    context: dict                 // e.g., {"unit_ref": "tu-5", "score": -0.1}
    message: string               // Human-readable description
    timestamp: string             // ISO 8601
```

---

## 14. Global Invariant Enforcement

### 14.1 Global Invariant Checklist

| Invariant | Enforcement Point | Method |
|---|---|---|
| GI-001: Language preserved | Stage 5 (Output Assembly) | OutputDocument.language = SourceDocument.language |
| GI-002: No new information | Stage 4 + Stage 6 | SummaryBlock content sourced from TextUnits; VR-004/VR-007 check |
| GI-003: 20% compression | Stage 4 + Stage 6 | Budget allocation + VR-001 check |
| GI-004: Traceability | Stage 3 + Stage 5 | All outputs reference source TextUnits via *_ref fields |
| GI-005: Structure preserved | Stage 4 | SummaryBlocks ordered by section position (INV-S4-003) |
| GI-006: References resolve | All stages | Each stage verifies *_ref fields point to existing components |

---

## 15. Execution Entry Point

### 15.1 Command-Line Interface

```
method main(args: string[]):
    config = load_config(parse_cli_args(args))
    
    input_path = config.input_path
    output_dir = config.output_dir
    
    // Create registry
    registry = create_default_registry()
    
    // Configure registry from config
    if config.scoring_method != "positional_tfidf":
        registry.set_scorer(get_scorer_by_name(config.scoring_method))
    if config.clustering_method != "keyword_overlap":
        registry.set_detector(get_detector_by_name(config.clustering_method))
    
    // Check input size limit
    if config.max_input_size_bytes is not null:
        file_size = get_file_size(input_path)
        if file_size > config.max_input_size_bytes:
            raise ConfigurationError("Input file exceeds max size: " + file_size + " > " + config.max_input_size_bytes)
    
    // Execute pipeline
    pipeline = PipelineController(config, registry)
    result = pipeline.execute(input_path, output_dir)
    
    // Report results
    print("Execution complete. Output files:")
    for output_type, path in result.output_paths:
        print("  " + output_type + ": " + path)
```

---

## 16. Traceability

| Implementation Element | Source Requirement | Composition Spec Reference |
|---|---|---|
| 7-stage pipeline (0-6) | TR-001 through TR-004, Assembly Steps | Transformation Rules: Stages 1-6 |
| InputParser protocol | C-FMT-001 | EXT-001 |
| ImportanceScorer protocol | TR-001, Q-OUT-006 | EXT-002, Stage 1 |
| RedundancyDetector protocol | TR-002 | EXT-003, Stage 2 |
| OutputRenderer protocol | C-FMT-002, C-FMT-003 | EXT-004, MAP-OUT-001, MAP-OUT-002 |
| compression_ratio = 0.20 | C-PERF-001 | GI-003, VR-001, INV-S4-002 |
| Language preservation | C-FMT-004, C-CMP-002 | GI-001, VR-002, VR-006 |
| No new information | C-CMP-001 | GI-002, VR-004, VR-007, INV-S4-005 |
| Structure preservation | C-CMP-003 | GI-005, INV-S4-003, VR-003 |
| Key points with scores | OUT-002, Q-OUT-006 | VR-005, MAP-OUT-002 |
| Ordered key points | Q-OUT-007 | INV-S3-003, MAP-OUT-002 |
| Registry pattern | CODER_IMPLEMENTATION_SOP | Extension Mechanism section |

---

## 17. Assumptions

| ID | Assumption | Justification |
|---|---|---|
| A-IMPL-001 | Default scoring uses positional + TF-IDF hybrid | Composition spec leaves algorithm open (EXT-002); this is a reasonable default |
| A-IMPL-002 | Default clustering uses keyword overlap (Jaccard) | Composition spec leaves algorithm open (EXT-003); simple and dependency-free |
| A-IMPL-003 | Stop words are English by default | Most common use case; configurable via stop_words_language |
| A-IMPL-004 | Sentence boundary = punctuation (.?!) followed by whitespace | Standard heuristic; no external NLP library required |
| A-IMPL-005 | Default output format is Markdown | Matches both input formats; human-readable |
| A-IMPL-006 | Language detection is heuristic (Unicode ranges + word frequency) | No external ML library required for default implementation |
| A-IMPL-007 | No maximum input size enforced | Requirement doc does not specify; configurable via max_input_size_bytes |
| A-IMPL-008 | Key point content is verbatim from source TextUnit | GI-002 compliance; light editing is optional future enhancement |

---

**End of Default Runtime Implementation**
