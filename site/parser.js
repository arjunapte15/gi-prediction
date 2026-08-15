// Fuzzy food matcher -- JS port of parser/meal_parser.py (Phase 11).
//
// This reproduces rapidfuzz's fuzz.WRatio scorer (ratio / partial_ratio /
// token_sort_ratio / token_set_ratio and their "partial" and "token" combos)
// closely enough that match outcomes agree with the Python implementation --
// ported directly from rapidfuzz's own pure-Python reference implementation
// (rapidfuzz/fuzz_py.py, rapidfuzz/distance/Indel_py.py), not reinvented.
// Score-cutoff based early-exit optimizations from that reference are
// dropped throughout: they only prune sub-computations that could not beat
// the running max, so omitting them changes performance, never the result.
//
// See parser/meal_parser.py for the return contract and matching rules this
// mirrors (RETURN CONTRACT, matching order, ambiguity detection rule).

(function (root) {
  const FUZZY_MATCH_THRESHOLD = 80;
  const AMBIGUITY_MARGIN = 10;

  // Mirrors rapidfuzz.utils.default_process: replace every character that
  // is not a Unicode letter/digit/underscore with a space, then trim and
  // lowercase (matches Python's `re.compile(r"(?ui)\W").sub(" ", s).strip().lower()`).
  function defaultProcess(s) {
    return s.replace(/[^\p{L}\p{N}_]/gu, " ").trim().toLowerCase();
  }

  // Mirrors Python's str.split() with no arguments: split on runs of
  // whitespace, discarding empty strings at the boundaries.
  function splitWords(s) {
    const t = s.trim();
    return t ? t.split(/\s+/) : [];
  }

  function sortedJoin(words) {
    return [...words].sort().join(" ");
  }

  // Longest common subsequence length. rapidfuzz uses a bit-parallel
  // variant for speed; a plain DP computes the exact same integer length.
  function lcsLength(a, b) {
    const n = a.length;
    const m = b.length;
    if (n === 0 || m === 0) return 0;
    let prev = new Array(m + 1).fill(0);
    for (let i = 1; i <= n; i++) {
      const cur = new Array(m + 1).fill(0);
      const ca = a[i - 1];
      for (let j = 1; j <= m; j++) {
        cur[j] = ca === b[j - 1] ? prev[j - 1] + 1 : Math.max(prev[j], cur[j - 1]);
      }
      prev = cur;
    }
    return prev[m];
  }

  // rapidfuzz.distance.Indel.distance: insertions+deletions only (no
  // substitution), derived from the LCS length.
  function indelDistance(a, b) {
    return a.length + b.length - 2 * lcsLength(a, b);
  }

  // rapidfuzz.fuzz.ratio: normalized Indel similarity, 0-100.
  function ratio(a, b) {
    const lensum = a.length + b.length;
    if (lensum === 0) return 100;
    return (1 - indelDistance(a, b) / lensum) * 100;
  }

  function normDistance(dist, lensum) {
    return lensum ? (1 - dist / lensum) * 100 : 100;
  }

  // Port of rapidfuzz's pure-Python `_partial_ratio_impl` (fuzz_py.py).
  // Assumes s1.length <= s2.length; finds the best-scoring alignment of s1
  // against a substring of s2 (including s1 overhanging s2's edges).
  function partialRatioImpl(s1, s2) {
    const len1 = s1.length;
    const len2 = s2.length;
    const s1CharSet = new Set(s1);
    let best = 0;

    for (let i = 1; i < len1; i++) {
      if (!s1CharSet.has(s2[i - 1])) continue;
      const r = ratio(s1, s2.slice(0, i));
      if (r > best) best = r;
    }

    for (let i = 0; i < len2 - len1; i++) {
      if (!s1CharSet.has(s2[i + len1 - 1])) continue;
      const r = ratio(s1, s2.slice(i, i + len1));
      if (r > best) best = r;
    }

    for (let i = len2 - len1; i < len2; i++) {
      if (!s1CharSet.has(s2[i])) continue;
      const r = ratio(s1, s2.slice(i));
      if (r > best) best = r;
    }

    return best;
  }

  // rapidfuzz.fuzz.partial_ratio_alignment's direction-selection logic,
  // score only (match_food never needs the alignment span).
  function partialRatio(s1, s2) {
    const len1 = s1.length;
    const len2 = s2.length;
    const shorter = len1 <= len2 ? s1 : s2;
    const longer = len1 <= len2 ? s2 : s1;

    let best = partialRatioImpl(shorter, longer);
    if (best !== 100 && len1 === len2) {
      const alt = partialRatioImpl(longer, shorter);
      if (alt > best) best = alt;
    }
    return best;
  }

  function tokenSortRatio(s1, s2) {
    return ratio(sortedJoin(splitWords(s1)), sortedJoin(splitWords(s2)));
  }

  function tokenSetRatio(s1, s2) {
    const tokensA = new Set(splitWords(s1));
    const tokensB = new Set(splitWords(s2));
    if (tokensA.size === 0 || tokensB.size === 0) return 0;

    const intersect = [...tokensA].filter((t) => tokensB.has(t));
    const diffAb = [...tokensA].filter((t) => !tokensB.has(t));
    const diffBa = [...tokensB].filter((t) => !tokensA.has(t));

    // one token set is a subset of the other
    if (intersect.length > 0 && (diffAb.length === 0 || diffBa.length === 0)) return 100;

    const diffAbJoined = sortedJoin(diffAb);
    const diffBaJoined = sortedJoin(diffBa);
    const abLen = diffAbJoined.length;
    const baLen = diffBaJoined.length;
    const sectLen = intersect.join(" ").length;

    const sectAbLen = sectLen + (sectLen !== 0 ? 1 : 0) + abLen;
    const sectBaLen = sectLen + (sectLen !== 0 ? 1 : 0) + baLen;

    const dist = indelDistance(diffAbJoined, diffBaJoined);
    const result = normDistance(dist, sectAbLen + sectBaLen);

    if (sectLen === 0) return result;

    const sectAbDist = (sectLen !== 0 ? 1 : 0) + abLen;
    const sectAbRatio = normDistance(sectAbDist, sectLen + sectAbLen);

    const sectBaDist = (sectLen !== 0 ? 1 : 0) + baLen;
    const sectBaRatio = normDistance(sectBaDist, sectLen + sectBaLen);

    return Math.max(result, sectAbRatio, sectBaRatio);
  }

  function tokenRatio(s1, s2) {
    return Math.max(tokenSetRatio(s1, s2), tokenSortRatio(s1, s2));
  }

  function partialTokenSortRatio(s1, s2) {
    return partialRatio(sortedJoin(splitWords(s1)), sortedJoin(splitWords(s2)));
  }

  function partialTokenSetRatio(s1, s2) {
    const tokensA = new Set(splitWords(s1));
    const tokensB = new Set(splitWords(s2));
    if (tokensA.size === 0 || tokensB.size === 0) return 0;
    if ([...tokensA].some((t) => tokensB.has(t))) return 100;

    const diffAb = sortedJoin([...tokensA].filter((t) => !tokensB.has(t)));
    const diffBa = sortedJoin([...tokensB].filter((t) => !tokensA.has(t)));
    return partialRatio(diffAb, diffBa);
  }

  function partialTokenRatio(s1, s2) {
    const splitA = splitWords(s1);
    const splitB = splitWords(s2);
    const tokensA = new Set(splitA);
    const tokensB = new Set(splitB);
    if ([...tokensA].some((t) => tokensB.has(t))) return 100;

    const diffAb = [...tokensA].filter((t) => !tokensB.has(t));
    const diffBa = [...tokensB].filter((t) => !tokensA.has(t));

    const result = partialRatio(sortedJoin(splitA), sortedJoin(splitB));

    if (splitA.length === diffAb.length && splitB.length === diffBa.length) return result;

    return Math.max(result, partialRatio(sortedJoin(diffAb), sortedJoin(diffBa)));
  }

  // rapidfuzz.fuzz.WRatio -- applies default_process itself, exactly as
  // rapidfuzz's `processor=` argument would when passed to process.extract.
  function wRatio(rawS1, rawS2) {
    const s1 = defaultProcess(rawS1);
    const s2 = defaultProcess(rawS2);
    if (!s1 || !s2) return 0;

    const UNBASE_SCALE = 0.95;
    const len1 = s1.length;
    const len2 = s2.length;
    const lenRatio = len1 > len2 ? len1 / len2 : len2 / len1;

    let endRatio = ratio(s1, s2);
    if (lenRatio < 1.5) {
      return Math.max(endRatio, tokenRatio(s1, s2) * UNBASE_SCALE);
    }

    const PARTIAL_SCALE = lenRatio <= 8.0 ? 0.9 : 0.6;
    endRatio = Math.max(endRatio, partialRatio(s1, s2) * PARTIAL_SCALE);

    return Math.max(endRatio, partialTokenRatio(s1, s2) * UNBASE_SCALE * PARTIAL_SCALE);
  }

  // Port of meal_parser.match_food. `records` is the foods.json array,
  // `aliases` is the food_aliases.json object (alias -> canonical food_name).
  function matchFood(query, records, aliases, threshold, ambiguityMargin) {
    threshold = threshold === undefined ? FUZZY_MATCH_THRESHOLD : threshold;
    ambiguityMargin = ambiguityMargin === undefined ? AMBIGUITY_MARGIN : ambiguityMargin;

    const recordsByName = new Map(records.map((r) => [r.food_name, r]));
    const foodNames = [...recordsByName.keys()];

    const queryNorm = query.trim().toLowerCase();
    if (!queryNorm) return { status: "not_found" };

    for (const name of foodNames) {
      if (name.trim().toLowerCase() === queryNorm) {
        return { status: "matched", food: recordsByName.get(name) };
      }
    }

    if (Object.prototype.hasOwnProperty.call(aliases, queryNorm)) {
      return { status: "matched", food: recordsByName.get(aliases[queryNorm]) };
    }

    const scoreByName = new Map();
    for (const name of foodNames) {
      const score = wRatio(queryNorm, name);
      if (score >= threshold) scoreByName.set(name, score);
    }
    if (scoreByName.size === 0) return { status: "not_found" };

    const topScore = Math.max(...scoreByName.values());
    const candidateNames = [...scoreByName.keys()]
      .filter((n) => scoreByName.get(n) >= topScore - ambiguityMargin)
      .sort((a, b) => scoreByName.get(b) - scoreByName.get(a) || (a < b ? -1 : a > b ? 1 : 0));

    if (candidateNames.length === 1) {
      return { status: "matched", food: recordsByName.get(candidateNames[0]) };
    }
    return { status: "ambiguous", candidates: candidateNames.map((n) => recordsByName.get(n)) };
  }

  const GIMatcher = { matchFood, wRatio, defaultProcess };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = GIMatcher;
  }
  if (root) {
    root.GIApp = root.GIApp || {};
    root.GIApp.matcher = GIMatcher;
  }
})(typeof window !== "undefined" ? window : undefined);
