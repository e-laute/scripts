# Usage: sh clone_and_update_repos.sh

# Install gh: brew install gh
# first time: gh auth login (either with token or with github credentials)

# https://stackoverflow.com/a/68770988
# https://cli.github.com/manual/


gh repo list e-laute --limit 1000 --no-archived --source | while read -r repo _; do
  # Skip if repo name starts with ARCHIVED or matches specific repos
  if [[ "$repo" == e-laute/ARCHIVED* ]] || \
     [[ "$repo" == "e-laute/e-laute.github.io" ]] || \
     [[ "$repo" == "e-laute/SPARQL" ]] || \
     [[ "$repo" == "e-laute/extra" ]] || \
     [[ "$repo" == "e-laute/Database-" ]] || \
     [[ "$repo" == "e-laute/DATABASE_TabHum" ]] || \
     [[ "$repo" == "e-laute/DATABASE-README" ]] || \
     [[ "$repo" == "e-laute/GH_Actions" ]] || \
     [[ "$repo" == "e-laute/.github-private" ]] || \
     [[ "$repo" == "e-laute/scripts" ]] || \
     [[ "$repo" == "e-laute/audio" ]] || \
     [[ "$repo" == "e-laute/validate_encodings" ]] || \
     [[ "$repo" == "e-laute/upload_mei_to_TU-RDM" ]] || \
     [[ "$repo" == "e-laute/.github" ]]; then
    echo "Skipping repository: $repo"
    continue
  fi

  echo "Processing repository: $repo"
  gh repo clone "$repo" /Users/jaklin/Desktop/E-LAUTE/"$repo" -- -q 2>/dev/null || (
    cd /Users/jaklin/Desktop/E-LAUTE/"$repo"
    # Handle case where local checkout is on a non-main/master branch
    # - ignore checkout errors because some repos may have zero commits,
    # so no main or master
    git checkout -q main 2>/dev/null || true
    git checkout -q master 2>/dev/null || true
    git pull -q
  )
done
