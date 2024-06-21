from Pipeline import Pipeline
from Phase import Phase
from clean.berlinkino import clean_berlinkino

def main():
    # Create pipeline and add phases
    pipeline = Pipeline("Berlinkino")
    pipeline.add_phase(Phase("Clean", clean_berlinkino))
    # pipeline.add_phase(Phase("Phase 2", execute_fn_2))
    # Add more phases as needed
   
    # Start pipeline
    pipeline.start()
    
    # Wait for pipeline to finish
    pipeline.join()

if __name__ == "__main__":
    main()