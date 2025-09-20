# Steam Playlog Recorder 
<small>(*Tkinter edition*)</small>

weird little utility to assist in manually recording "playlogs" that record over time when you've last played a game and for how long. super useful if you're possibly borderline OCD or some shit liek me lmao. i wrote it for myself, mostly, albeit with delusions of grandeur of public use.

it reads/writes to & from text files in an own format that can probably best be described as "an ill-thought out YAML wannabe". it is intentionally, excessively, forgiving of errors to the point of overcomplicating the design & implementation.

the code is a tangled hot mess which probably serves as proof that not only should I never again be allowed to design or develop or even conceive programs, but that i am fundamentally incapable of getting even something stupidly simple that I want to get done, done.

run it from anywhere (playlogs folder is currently hardcoded...); uses only standard libraries & should work in any recent Python 3 version (tested & developed in 3.10.2, requires at least 3.6 at minimum due to f-strings and os.DirEntry usage)

lot of features missing or incomplete or possibly buggy. sorry.
