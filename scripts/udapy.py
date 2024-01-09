#import gc
import sys
sys.path.insert( 1, '../udapi-python')
from udapi.core.run import Run

data = "../data"
name = "UD_pud_test.CS"

args = "read.Conllu files=" + data + "/m_conllu/" + name + ".conllu"
      #valency.Cs_frame_extractor \
      #    output_folder="$data"/ext_pic/ \
      #    output_name="$name"

# Process and provide the scenario.
if __name__ == "__main__":
#    gc.disable()

    runner = Run( args)
    # udapy is often piped to head etc., e.g.
    # `seq 1000 | udapy -s read.Sentences | head`
    # Let's prevent Python from reporting (with distracting stacktrace)
    # "BrokenPipeError: [Errno 32] Broken pipe"
    runner.execute()