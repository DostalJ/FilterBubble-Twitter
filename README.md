# FilterBubble-Twitter
Software to study effects of filter bubble on twitter.

### Basic Usage
To sample ```n``` followers of twitter page:
```
python3 collect_followers.py -p=TwitterPage -n=100 -o=path_to_save_file
```
To start streaming and saving measured data:
```
python3 script.py -p=file_with_ids_of_interest -k=keyword -o=file_to_save_results_to
```
