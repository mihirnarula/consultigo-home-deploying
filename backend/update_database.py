from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Problem, ProblemExample, Framework, DifficultyLevel
from app.database import SQLALCHEMY_DATABASE_URL
import os

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Sample frameworks data
sample_frameworks = [
    # Market Entry frameworks
    {
        "problem_id": 1,  # Assuming this is a Market Entry problem
        "title": "Porter's Five Forces",
        "content": """
# Porter's Five Forces Framework

Porter's Five Forces is a framework for analyzing a company's competitive environment. The five forces are:

1. **Threat of new entrants:** How easy is it for new competitors to enter the market?
2. **Bargaining power of suppliers:** How much control do suppliers have over prices?
3. **Bargaining power of buyers:** How much control do customers have over prices?
4. **Threat of substitute products:** How easily can customers find alternatives?
5. **Competitive rivalry:** How intense is the competition among existing companies?

## How to Apply:
1. Start by defining the industry and scope of analysis
2. Analyze each force systematically
3. Consider how each force impacts profitability
4. Develop recommendations based on your analysis

## Example Application:
For a market entry case, assess whether the target market has high entry barriers (good for incumbents) or low barriers (good for new entrants). Evaluate supplier concentration, buyer sensitivity to price, availability of substitutes, and competitive intensity to determine overall market attractiveness.
        """
    },
    {
        "problem_id": 1,
        "title": "PESTEL Analysis",
        "content": """
# PESTEL Analysis Framework

PESTEL is a framework used to analyze the external macro-environmental factors that might impact an organization. PESTEL stands for:

1. **P**olitical: Government policies, political stability, trade regulations
2. **E**conomic: Economic growth, interest rates, inflation, unemployment
3. **S**ocial: Cultural trends, demographics, lifestyle changes
4. **T**echnological: Technological advancements, R&D activity, automation
5. **E**nvironmental: Climate change, environmental policies, sustainability
6. **L**egal: Laws affecting business operations, consumer protection, employment laws

## How to Apply:
1. Identify relevant factors in each category
2. Assess each factor's impact (positive/negative) and importance
3. Determine which factors are most critical for the specific market
4. Develop strategic recommendations based on your analysis

## Example Application:
In a market entry case, analyze political stability, economic conditions, social acceptance of your product, technological infrastructure, environmental considerations, and legal requirements in the target market to identify potential opportunities and threats.
        """
    },
    
    # Profitability frameworks
    {
        "problem_id": 2,  # Assuming this is a Profitability problem
        "title": "Profit Tree",
        "content": """
# Profit Tree Framework

The Profit Tree framework breaks down a company's profit into its components to identify areas for improvement.

## Basic Structure:
- **Profit** = Revenue - Costs
  - **Revenue** = Price × Volume
    - **Price** factors: product mix, pricing strategy, discounts
    - **Volume** factors: market size, market share, customer retention
  - **Costs** = Fixed Costs + Variable Costs
    - **Fixed Costs**: rent, salaries, equipment
    - **Variable Costs**: raw materials, production costs, commissions

## How to Apply:
1. Draw out the profit tree
2. Identify which branches have declined or need improvement
3. Drill down on problem areas
4. Quantify the impact of each element when possible
5. Develop recommendations to address root causes

## Example Application:
In a profitability case, systematically walk through each component of the profit equation to identify if the issue is related to pricing, volume, fixed costs, or variable costs. Then focus on the specific drivers that contribute to the problem area.
        """
    },
    {
        "problem_id": 2,
        "title": "3C Analysis",
        "content": """
# 3C Analysis Framework

The 3C Analysis provides a strategic look at the factors needed for success. The three Cs stand for:

1. **Company**: Internal capabilities, resources, and positioning
2. **Customers**: Target market needs, behaviors, and segments
3. **Competitors**: Competitive landscape, market shares, and strategies

## How to Apply:
1. Analyze each C separately:
   - **Company**: Assess strengths, weaknesses, and competitive advantages
   - **Customers**: Identify needs, segments, and trends
   - **Competitors**: Map out direct and indirect competitors
2. Identify areas of alignment or misalignment
3. Find opportunities where the company can better serve customers or differentiate from competitors

## Example Application:
For a profitability case, examine how well the company's capabilities align with customer needs, and how the company compares to competitors. Look for gaps in the market or areas where the company has a unique advantage that could be leveraged to improve profitability.
        """
    },
    
    # Growth Strategy frameworks
    {
        "problem_id": 3,  # Assuming this is a Growth Strategy problem
        "title": "Ansoff Matrix",
        "content": """
# Ansoff Matrix Framework

The Ansoff Matrix is a strategic planning tool that provides a framework to devise strategies for growth by focusing on whether to market new or existing products in new or existing markets.

## Four Growth Strategies:
1. **Market Penetration**: Existing products in existing markets (lowest risk)
2. **Market Development**: Existing products in new markets
3. **Product Development**: New products in existing markets
4. **Diversification**: New products in new markets (highest risk)

## How to Apply:
1. Identify where the company is currently operating
2. Assess the risk appetite and resources of the company
3. Evaluate the growth potential of each strategy
4. Select the most appropriate strategy based on company goals and capabilities

## Example Application:
In a growth strategy case, evaluate which quadrant offers the best opportunity given the company's resources and market conditions. For example, a company with strong market presence might focus on product development, while one with excellent products but market saturation might pursue market development.
        """
    },
    {
        "problem_id": 3,
        "title": "BCG Matrix",
        "content": """
# BCG Matrix Framework

The BCG (Boston Consulting Group) Matrix is a framework that categorizes a company's products or business units based on their market growth rate and market share.

## Four Categories:
1. **Stars**: High growth, high market share - require investment to maintain leadership
2. **Cash Cows**: Low growth, high market share - generate cash to fund other initiatives
3. **Question Marks**: High growth, low market share - require significant investment to grow
4. **Dogs**: Low growth, low market share - consider divesting or repositioning

## How to Apply:
1. Plot each product or business unit on the matrix
2. Analyze the current portfolio balance
3. Determine appropriate strategies for each category
4. Develop a plan to optimize resource allocation

## Example Application:
For a growth strategy case, map the company's products/services onto the BCG matrix to identify which ones should receive investment for growth, which should be maintained for cash generation, and which might need to be reconsidered. This helps prioritize where to focus growth efforts.
        """
    },
    
    # M&A frameworks
    {
        "problem_id": 4,  # Assuming this is an M&A problem
        "title": "Synergy Analysis",
        "content": """
# Synergy Analysis Framework

A framework for evaluating potential synergies in mergers and acquisitions to determine if the combined entity will create more value than the sum of its parts.

## Types of Synergies:
1. **Cost Synergies**:
   - Economies of scale
   - Reduction in overhead
   - Operational efficiencies
   - Supply chain optimization

2. **Revenue Synergies**:
   - Cross-selling opportunities
   - Geographic expansion
   - Combined product offerings
   - Increased market power

## How to Apply:
1. Identify potential synergies in both cost and revenue categories
2. Quantify the expected value of each synergy
3. Assess the timeline and probability of achieving each synergy
4. Calculate the net present value of all synergies
5. Compare to the acquisition premium to determine if the deal creates value

## Example Application:
In an M&A case, systematically evaluate which costs can be eliminated (duplicate functions, facilities) and which revenue opportunities might be created (cross-selling, new markets). Quantify these benefits and compare them to the cost of acquisition to determine if the deal makes financial sense.
        """
    },
    {
        "problem_id": 4,
        "title": "Due Diligence Framework",
        "content": """
# Due Diligence Framework

A comprehensive framework for assessing a target company before an acquisition to identify risks and opportunities.

## Key Areas to Evaluate:
1. **Strategic Fit**:
   - Business model alignment
   - Cultural compatibility
   - Long-term strategic goals

2. **Financial Analysis**:
   - Historical performance
   - Projections and assumptions
   - Debt and capital structure

3. **Operational Assessment**:
   - Production capabilities
   - Supply chain efficiency
   - Technology systems

4. **Human Capital**:
   - Management team quality
   - Employee capabilities
   - Retention risks

5. **Legal and Regulatory**:
   - Outstanding litigation
   - Compliance issues
   - Regulatory approvals required

## How to Apply:
1. Develop a checklist for each key area
2. Gather information through documents and interviews
3. Identify red flags and potential deal-breakers
4. Assess impact on valuation and integration planning

## Example Application:
For an M&A case, conduct a thorough evaluation of the target company across all dimensions to uncover hidden risks or opportunities that might affect the acquisition decision or price. This helps ensure that the acquirer has complete information before proceeding.
        """
    }
]

# Sample examples data
sample_examples = [
    # Market Entry examples
    {
        "problem_id": 1,
        "example_text": "A luxury clothing brand is considering entering the Indian market. Should they proceed?",
        "example_answer": """
# Market Entry Analysis for Luxury Clothing Brand in India

## Market Sizing
- India's population: ~1.4 billion
- Middle and upper class: ~300 million
- Luxury consumers: ~30 million (10% of middle/upper class)
- Potential market: $10 billion luxury fashion industry in India

## PESTEL Analysis
- **Political**: Stable government, favorable foreign investment policies
- **Economic**: Growing GDP, expanding middle class, increasing disposable income
- **Social**: Growing aspirational class, increasing brand consciousness
- **Technological**: Rising e-commerce penetration, social media influence
- **Environmental**: Increasing focus on sustainability
- **Legal**: Import duties on luxury goods (20-25%)

## Porter's Five Forces
- **Competitive Rivalry**: Moderate (existing luxury brands present but market growing)
- **Threat of New Entrants**: Moderate (high capital requirements but growing market)
- **Supplier Power**: Low-Moderate (multiple production options)
- **Buyer Power**: Moderate (price sensitivity varies by segment)
- **Threat of Substitutes**: Low (limited substitutes for luxury fashion)

## Recommendation
Proceed with market entry through a phased approach:
1. Start with e-commerce platform and presence in luxury malls in major cities (Delhi, Mumbai, Bangalore)
2. Tailor some products to Indian preferences and occasions (e.g., wedding collections)
3. Develop targeted marketing strategy highlighting brand heritage and exclusivity
4. Expand to tier-2 cities as brand awareness grows
        """
    },
    
    # Profitability example
    {
        "problem_id": 2,
        "example_text": "A restaurant chain has seen declining profits over the past year despite stable revenues. What could be causing this issue?",
        "example_answer": """
# Profitability Analysis for Restaurant Chain

## Profit Tree Analysis
Since revenue has remained stable, I'll focus on cost factors:

### Fixed Costs:
- **Rent**: Have any locations been renegotiated or moved to higher-cost areas?
- **Labor**: Have minimum wage increases affected staffing costs?
- **Equipment**: Has there been investment in new equipment/technology?

### Variable Costs:
- **Food Costs**: Have ingredient prices increased?
- **Energy**: Have utility costs risen?
- **Packaging**: Have takeout/delivery packaging costs increased?

## Key Findings
After analysis, the following issues were identified:
1. **Food Cost Inflation**: 15% increase in key ingredients (meat, dairy) without menu price adjustments
2. **Labor Costs**: 10% increase due to minimum wage increases and higher turnover requiring training costs
3. **Delivery Costs**: 8% increase in delivery-related expenses as more customers order online

## Recommendations
1. **Menu Engineering**: Redesign menu to highlight high-margin items, adjust prices selectively
2. **Supplier Negotiation**: Seek volume discounts or alternative suppliers for key ingredients
3. **Labor Optimization**: Implement scheduling software to optimize staffing levels based on demand
4. **Delivery Strategy**: Renegotiate terms with delivery platforms or develop in-house delivery solution
5. **Energy Efficiency**: Invest in energy-efficient equipment to reduce utility costs

## Expected Impact
Implementing these recommendations could improve profit margins by 4-6% within 6 months.
        """
    },
    
    # Growth Strategy example
    {
        "problem_id": 3,
        "example_text": "A successful educational software company focused on K-12 schools wants to grow its business. What growth strategies should they consider?",
        "example_answer": """
# Growth Strategy for Educational Software Company

## Current Situation Analysis
- Successful in K-12 schools market
- Strong product offering and reputation
- Market is competitive but company has established presence

## Growth Options Using Ansoff Matrix

### Market Penetration (Existing products, Existing market)
- **Opportunities**:
  - Increase market share in current K-12 segment
  - Deepen relationships with existing school districts
  - Upsell premium features to current customers
- **Implementation**:
  - Enhanced sales team focused on district-wide adoptions
  - Customer success program to ensure renewal and expansion
  - Referral incentives for existing customers

### Market Development (Existing products, New markets)
- **Opportunities**:
  - Expand to international English-speaking education markets
  - Enter adjacent markets (private tutoring centers, homeschooling)
  - Target higher education institutions
- **Implementation**:
  - Localization strategy for key international markets
  - Partnerships with tutoring chains and homeschool associations
  - Modified product offerings for college readiness

### Product Development (New products, Existing market)
- **Opportunities**:
  - Develop complementary products (assessment tools, parent engagement apps)
  - Create specialized offerings for STEM, arts, or special education
  - Build administrative tools for school management
- **Implementation**:
  - Product development roadmap based on customer feedback
  - Acquisition of complementary technologies
  - Beta testing program with loyal customer base

### Diversification (New products, New markets)
- **Opportunities**:
  - Corporate training software
  - Adult continuing education platform
  - Consumer educational apps
- **Implementation**:
  - Start with adjacent areas that leverage core capabilities
  - Consider separate brand/division for non-K-12 offerings
  - Potential partnerships or acquisitions to accelerate entry

## Recommendation
Pursue a staged approach:
1. **Short-term** (0-12 months): Market Penetration + Product Development
   - Focus on increasing share in existing market
   - Develop 1-2 complementary products for current customers
2. **Medium-term** (1-2 years): Market Development
   - Expand to international markets and adjacent segments
3. **Long-term** (2+ years): Consider Selective Diversification
   - Evaluate opportunities in corporate or adult education
        """
    },
    
    # M&A example
    {
        "problem_id": 4,
        "example_text": "A large telecommunications company is considering acquiring a smaller fiber internet provider. How would you evaluate this potential acquisition?",
        "example_answer": """
# M&A Evaluation: Telecom Acquisition of Fiber Provider

## Strategic Rationale Assessment
- **Market Position**: Acquisition would strengthen broadband offerings
- **Technology Stack**: Fiber technology complements existing infrastructure
- **Geographic Footprint**: Does target provide access to new regions?
- **Customer Base**: Does target bring valuable customer segments?

## Financial Analysis
- **Valuation Metrics**:
  - Industry average: 6-8x EBITDA
  - Growth premium: +1-2x for high-growth fiber companies
  - Appropriate range: $X-Y million based on financials
- **Historical Performance**:
  - Revenue CAGR: ~15% over past 3 years
  - EBITDA margin: ~30% (improving)
  - Capex requirements: Significant but declining
- **Projected Performance**:
  - Revenue synergies: $20-30M annually by year 3
  - Cost synergies: $15-25M annually by year 2

## Synergy Analysis
- **Cost Synergies**:
  - Network operations consolidation: $8-10M
  - Overhead reduction: $4-6M
  - Procurement efficiencies: $3-5M
  - Technology integration: $3-4M
- **Revenue Synergies**:
  - Cross-selling opportunities: $10-15M
  - Enhanced service offerings: $8-12M
  - Reduced customer churn: $5-8M

## Integration Considerations
- **Technical Integration**:
  - Network systems compatibility
  - OSS/BSS integration complexity
  - Timeline: 12-18 months
- **Organizational Integration**:
  - Cultural alignment assessment
  - Retention of key technical talent
  - Leadership structure post-acquisition
- **Regulatory Considerations**:
  - Antitrust review likelihood
  - Regulatory approvals timeline

## Risk Assessment
- **Integration Risks**:
  - Technical integration challenges
  - Customer service disruption
  - Employee retention
- **Market Risks**:
  - Competitive response
  - Technology obsolescence
  - Regulatory changes

## Recommendation
Based on the analysis, recommend proceeding with the acquisition with the following conditions:
1. Valuation not to exceed 7.5x EBITDA plus synergy adjustments
2. Retention packages for key technical and leadership talent
3. Phased integration approach prioritizing customer experience
4. Clear milestone-based plan for capturing identified synergies
        """
    }
]

try:
    # Add frameworks to database
    for framework_data in sample_frameworks:
        # Check if framework already exists
        existing_framework = db.query(Framework).filter(
            Framework.problem_id == framework_data["problem_id"],
            Framework.title == framework_data["title"]
        ).first()
        
        if not existing_framework:
            new_framework = Framework(
                problem_id=framework_data["problem_id"],
                title=framework_data["title"],
                content=framework_data["content"]
            )
            db.add(new_framework)
    
    # Add examples to database
    for example_data in sample_examples:
        # Check if example already exists
        existing_example = db.query(ProblemExample).filter(
            ProblemExample.problem_id == example_data["problem_id"],
            ProblemExample.example_text == example_data["example_text"]
        ).first()
        
        if not existing_example:
            new_example = ProblemExample(
                problem_id=example_data["problem_id"],
                example_text=example_data["example_text"],
                example_answer=example_data["example_answer"]
            )
            db.add(new_example)
    
    db.commit()
    print("Successfully added frameworks and examples to database!")
    
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
    
finally:
    db.close() 