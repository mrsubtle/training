import os
import json
import argparse
from subprocess import call

parser = argparse.ArgumentParser()
parser.add_argument('--steps', type=int, default=300)
args = parser.parse_args()

annotations_file = os.path.join('.tmp', '_annotations.json')

with open(annotations_file) as f:
  annotations_type = json.load(f)['type']

if annotations_type == 'localization':
  execution_command = """
    export PYTHONPATH=`pwd`/slim &&
    python3 -m object_detection.model_main \
      --pipeline_config_path=${RESULT_DIR}/pipeline.config \
      --model_dir=${RESULT_DIR}/checkpoint \
      --num_train_steps=""" + str(args.steps) + """ \
      --alsologtostderr &&
    python3 -m scripts.quick_export_graph \
      --result_base=${RESULT_DIR} \
      --model_dir=${RESULT_DIR}/model &&
    python3 -m scripts.convert --tfjs --coreml \
      --tfjs-path=${RESULT_DIR}/model_web \
      --mlmodel-path=${RESULT_DIR}/model_ios \
      --exported-graph-path=${RESULT_DIR}/model
  """
else:
  execution_command = """
    python3 -m classification.retrain \
      --image_dir=${RESULT_DIR}/data \
      --saved_model_dir=${RESULT_DIR}/model/saved_model \
      --tfhub_module=https://tfhub.dev/google/imagenet/mobilenet_v1_100_224/feature_vector/1 \
      --how_many_training_steps=""" + str(args.steps) + """ \
      --output_labels=${RESULT_DIR}/model/labels.txt &&
    python3 -m scripts.convert --coreml --tflite \
      --mlmodel-path=${RESULT_DIR}/model_ios \
      --tflite-path=${RESULT_DIR}/model_android \
      --exported-graph-path=${RESULT_DIR}/model
  """

call(execution_command, shell=True)