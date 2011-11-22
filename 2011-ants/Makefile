clean: 
	if [ -d "target" ]; then \
		rm -rf target; \
	fi
	rm -rf src/*~;
	
init:
	if [ ! -d "target" ]; then \
		mkdir target; \
	fi

tools: init
	if [ ! -d "target/tools" ]; then \
		wget http://aichallenge.org/tools.tar.bz2 -O target/tools.tar.bz2; \
		tar -xf target/tools.tar.bz2 --directory=target; \
	fi

package: tools
	cp src/* target;
	cp ../aichallenge/ants/dist/starter_bots/python/ants.py ./target;

test: package
	more target/test_input.txt | python target/MyBot.py;

run: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/example/tutorial1.map "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/random_walk/random_walk_04p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-big: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/random_walk/random_walk_08p_02.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-maze: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_02p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-maze-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_04p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \
