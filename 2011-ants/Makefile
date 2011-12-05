clean: 
	if [ -d "target" ]; then \
		rm -rf target; \
	fi
	rm -rf src/*~;
	
init:
	if [ ! -d "target" ]; then \
		mkdir target; \
	fi

download: init
	if [ ! -d "target/tools" ]; then \
		wget http://aichallenge.org/tools.tar.bz2 -O target/tools.tar.bz2; \
		tar -xf target/tools.tar.bz2 --directory=target; \
	fi
	if [ ! -d "target/v6" ]; then \
        wget https://github.com/papousek/aichallenge-eskymobot/zipball/v6 -O target/v6.zip; \
        unzip target/v6.zip -d target; \
        mv target/papousek-aichallenge-eskymobot-6d2f96f target/v6; \
        mkdir target/v6/2011-ants/target; \
        cp target/v6/2011-ants/src/* target/v6/2011-ants/target; \
        cp ../aichallenge/ants/dist/starter_bots/python/ants.py target/v6/2011-ants/target; \
    fi
	if [ ! -d "target/v7" ]; then \
        wget https://github.com/papousek/aichallenge-eskymobot/zipball/v7 -O target/v7.zip; \
        unzip target/v7.zip -d target; \
        mv target/papousek-aichallenge-eskymobot-4b5881e target/v7; \
        mkdir target/v7/2011-ants/target; \
        cp target/v7/2011-ants/src/* target/v7/2011-ants/target; \
        cp ../aichallenge/ants/dist/starter_bots/python/ants.py target/v7/2011-ants/target; \
    fi

package: download
	cp src/* target;
	cp ../aichallenge/ants/dist/starter_bots/python/ants.py ./target;

test: package
	more target/test_input.txt | python target/MyBot.py;

run: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/example/tutorial1.map "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/example/tutorial1.map "python target/v7/2011-ants/target/MyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old-revert: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/example/tutorial1.map "python target/MyBot.py" "python target/v7/2011-ants/target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/random_walk/random_walk_04p_01.map "python target/v6/2011-ants/target/MyBot.py" "python target/v6/2011-ants/target/MyBot.py" "python target/v7/2011-ants/target/MyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old-maze: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_02p_01.map "python target/v7/2011-ants/target/MyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old-maze-revert: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_02p_01.map "python target/MyBot.py" "python target/v7/2011-ants/target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-old-maze-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_04p_01.map "python target/v7/2011-ants/target/MyBot.py" "python target/v7/2011-ants/target/MyBot.py" "python target/v7/2011-ants/target/MyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/random_walk/random_walk_04p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-big: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/random_walk/random_walk_08p_02.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-maze: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_02p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \

run-maze-medium: package
	target/tools/playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir target/game_logs --turns 1000 --map_file target/tools/maps/maze/maze_04p_01.map "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/HunterBot.py" "python target/tools/sample_bots/python/GreedyBot.py" "python target/MyBot.py" -So | java -jar target/tools/visualizer.jar; \
