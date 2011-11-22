import sys
import traceback

class Strategy:
	
    def __init__(self):
        pass
	
    def run(self, bot, driver):
        map_data = ''		
        while(True):
            try:
                current_line = sys.stdin.readline().rstrip('\r\n') # string new line char
                if current_line.lower() == 'ready':
                    driver.setup(map_data)
                    bot.do_setup(driver)
                    driver.finish_turn()
                    map_data = ''
                elif current_line.lower() == 'go':
                    driver.update(map_data)
                    # call the do_turn method of the class passed in
                    bot.do_turn()
                    driver.finish_turn()
                    map_data = ''
                else:
                    map_data += current_line + '\n'
            except EOFError:
                break
            except KeyboardInterrupt:
                raise
            except:
                # don't raise error or return so that bot attempts to stay alive
                traceback.print_exc(file=sys.stderr)
                sys.stderr.flush()
