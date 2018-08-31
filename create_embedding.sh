#!/bin/bash

data="$1"
path="$2"
prefix="temporary_embedding"
temp_dir="data/tech/temp_embedding"

if [ -z "$data" ] || [ -z "$path" ] 
then
	echo "Provide 2 arguments: file with list of files and path to them."
	exit
fi

python3 python/extractor/ExtractFromPython.py tokens "$prefix" "$data" "$path"
python3 python/TokensToTopTokens.py "$prefix" data/tech/tokens_${prefix}_*.json
mkdir "$temp_dir"
mv data/tech/token_to_number_${prefix}_*.json "$temp_dir"
mv data/tech/encoded_tokens_${prefix}_*.json "$temp_dir"
rm data/tech/tokens_${prefix}_*.json
python3 python/EmbeddingLearnerWord2Vec.py "$prefix" ${temp_dir}/token_to_number_${prefix}_*.json ${temp_dir}/encoded_tokens_${prefix}_*.json
rm $temp_dir/*.json
rm -d "$temp_dir"
mv data/tech/embedding_model_${prefix}* data/tech/embedding_model_created
mv data/tech/token_to_vector_${prefix}* data/tech/token_to_vector_created

