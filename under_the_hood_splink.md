
Let 
- pi as the probability that two random records match, 
- u probability (u prob) as the probability that a certain field agrees for a non-match pair,
    - P(field agrees | non-match)
- m probability (m prob) as the probability that a certain fields agree for a match pair.
    - P(field agrees | match)

Overall, pi, m and u probabilities are initially estimated, match probability is calculated in the Expectation step, and updated. 

**1. Estimate initial pi**  
- Using deterministic rules, estimate pi.
- Deterministic rules are rules by which we can determine if a pair is a match.
- For instance, if first name, last name and date of birth are same for a pair, the pair is set to be a match.

**2. Estimate initial u prob**
- Estimate initial u prob value from random sampling.
- If you're to randomly draw a sample pair, it's likely that the pair is not a match due to very low pi value.
- Assuming that the pair is not a match, if the fields agree, then you can calculate the u prob.

**3. Estimate initial m prob**
- Estimate initial m prob value using labelled column (e.g., NI Number, Unique Pupil Number).
- If the labelled column agrees in a pair, then the pair is a match.
- With this confirmed match, you calculate if fields agree, which gives you the m prob of each field.

**4. First Expectation Step (E-Step)**
- With the current estimates of m, u and pi probs, match score is calculated for each pair. 
- Match score would be the sum of log10(m/u) from all fields.
- Match probability then can be calculated: 1/(1+10^(-score)) = 10^score / (1 + 10^score)

**5. First Maximisation Step (M-Step)**
- In the first M-Step, you apply blocking rules sequentially.
  - In blocking, you lock in a field (e.g., last name).
  - Instead of looking at all confirmed pairs, you look at each last name (e.g., Smith).
  - For each block, you calculate m and u probabilities.
  - You then calculate a summary m and u probability values, such as weighted average, of each field.
- In this initial M-step, you get updated m and u probs as well as updated pi, which is the average of match probability calculated in the first E-step.

**6. Second E-Step**
- Given the updated m, u and pi values in the initial M-step, you re-calculate the match score and accordingly match probability of each pair.

**7. Second M-Step**
- With the updated match probability, apply the blocking rules again. 
- This will update m and u probs and pi will be also updated using the match probability from second E-step.

**8. EM Convergence**
- These iterations of E & M steps continue until the parameter values stop changing.
- In other words, when the largest change across all parameters (`max(|delta_m_firstname|, |delta_m_lastname|, |delta_u_firstname|, |delta_u_lastname|, |delta_pi|)`) is smaller than `em_convergence` value defined in settings, the iteration stops.  
- As a result, the linker is trained, with final m, u and pi probs. 

**9. Predict**
- For each pair of records, you calculate match score and match probability using the final m and u values. 
- If the match probability is higher than the threshold, the pair is included in results. Otherwise, the pair is excluded.

_____

**Connecting m and u probabilities with comparison level**
- Both u and m probabilities are calculated using comparison levels, both before or after blocking.
- For instance, assume there are three comparison levels for first name: exact match, fuzzy match and all other. 
- For John vs John, exact match level will be applied, while for John vs Jon, fuzzy match level will be used and all other level will be used for John v Jane. 

____
**Connecting Bayes Theorem with match score**
- Bayes Theorem states that $P(A|B) = \frac{P(B|A) \cdot P(A)}{P(B)}$.
- In Splink, what we want is the probability that the pair is a match given its data: $P(\text{match}|\text{data}) = \frac{P(\text{data}|\text{match}) \cdot P(\text{match})}{P(\text{data})}$. 
   - Here, $P(\text{data}|\text{match}) = P(\text{first name agrees}|\text{match}) \times P(\text{last name agrees}|\text{match}) \times \ldots = m_{\text{firstname}} \times m_{\text{lastname}} \times \ldots$
   - Hence, $P(\text{data}|\text{match})$ is the product of all m probabilites of each field.
   - Also, $P(\text{match})$ is $\pi$, by definition.
   - Likewise, $P(\text{data}|\text{non-match}) = P(\text{first name agrees}|\text{non-match}) \times P(\text{last name agrees}|\text{non-match}) \times \ldots = u_{\text{firstname}} \times u_{\text{lastname}} \times \ldots$
   - Hence, $P(\text{data}|\text{non-match})$ is the product of all u probabilites of each field.
   - $P(\text{non-match}) = 1 - P(\text{match}) = 1 - \pi$
- We want to calculate the ratio between $P(\text{match}|\text{data}) / P(\text{non-match}|\text{data})$.
   - With the definitions above, the ratio equates to $\frac{P(\text{data}|\text{match}) \cdot \pi}{P(\text{data}|\text{non-match}) \cdot (1-\pi)}$.
   - If we take $\log_{10}$ of both sides, then: $\log_{10}\left(\frac{P(\text{match}|\text{data})}{P(\text{non-match}|\text{data})}\right) = \log_{10}\left(\frac{P(\text{data}|\text{match})}{P(\text{data}|\text{non-match})}\right) + \log_{10}\left(\frac{\pi}{1-\pi}\right)$.
   - For each pair, $\log_{10}\left(\frac{\pi}{1-\pi}\right)$ is constant. Hence, only the first term is used to calculate match score.
   - Essentially the term equates to the sum of $\log_{10}\left(\frac{m_i}{u_i}\right)$, where $m_i$ is the m prob for each field and $u_i$, u prob for each field.
