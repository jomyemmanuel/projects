#include <graphics.h>

// gcc matchThePairs.c -lgraph
// controls: w=>up, s=>down, a=>left, d=>right, q=>quit , spacebar=>select cell

int N=4; // size
int a[4][4]; // red selection mark
int b[4][4]; // store random nos
int c[4][4]; // visited or not
int d[16]={4,3,7,5,2,1,6,8,7,3,8,4,1,5,2,6}; // random nos from [1-8]
int point=0; // score
int u=-1,v=-1; //compare
char str[15]; // store score
int end=0; //end

void rec(){ // draw white rectangles
	int i,j;
	cleardevice();
	setcolor(WHITE);
	for(i=0;i<N;i++)
		for(j=0;j<N;j++)
			rectangle(100+(j*80),100+(i*80),140+(j*80),140+(i*80));
}

void set(int a, int b){ // red marker selection
	setcolor(RED);
	rectangle(90+(b*80),90+(a*80),150+(b*80),150+(a*80));
}

void printno(int u, int v){ // print nos in selected cell
	char no[15];
	sprintf(no, "%d", b[u][v]);
	outtextxy(120+(v*80), 120+(u*80), no);
}

void score(){ // print score
	outtextxy(150, 50, " MATCH THE PAIRS ");
	sprintf(str, "%d", point);
	outtextxy(450, 50, "Score:");
	outtextxy(450, 70, str);
}

void valid(){ // After clearing display, display all those matched cells.
	int i,j;
	end=0;
	for(i=0;i<N;i++)
		for(j=0;j<N;j++){
			if(c[i][j]==1)
				printno(i,j);
			else
				end=1;
		}
	score();
}

void compare(int i, int j){ // compare currently selected and previously selected cells
	if(b[i][j]!=b[u][v]){
		c[i][j]=-1;
		c[u][v]=-1;
	}
	u=-1; v=-1;
}

void check(char m){ // check character entered and update display accordingly
	int i,j,br=0;
	for(i=0;i<N;i++){
		for(j=0;j<N;j++){
			if(a[i][j]==0){
				br=1;
				break;
			}
		}
		if(br==1)
			break;
	}

	if(m=='d' && (j+1)<N){ // right
		a[i][j]=-1;
		a[i][j+1]=0;
		rec();
		set(i,j+1);
	}
	else if(m=='a' && (j-1)>=0){ // left
		a[i][j]=-1;
		a[i][j-1]=0;
		rec();
		set(i,j-1);
	}
	else if(m=='w' && (i-1)>=0){ // up
		a[i][j]=-1;
		a[i-1][j]=0;
		rec();
		set(i-1,j);
	}
	else if(m=='s' && (i+1)<N){ // down
		a[i][j]=-1;
		a[i+1][j]=0;
		rec();
		set(i+1,j);
	}
	else if(m==' '){ // A cell is selected
		if(c[i][j]!=1){
			point++;
			c[i][j]=1;
			if(u!=-1 && v!=-1){
				printno(i,j);
				delay(500);
				compare(i,j);
			}
			else{
				u=i; v=j;
			}
		}
		rec();
		set(i,j);
	}
	else{ // refresh display
		rec();
		set(i,j);
	}
	valid();
}

void swap(int j){ // perform random swapping
	int t;
	if(j!=0){
		t=d[j];
		d[j]=d[j-1];
		d[j-1]=t;
	}
	if(j!=15){
		t=d[j];
		d[j]=d[j+1];
		d[j+1]=t;
	}
}

void initialise(){
	int i,j,t=0;
	for(i=1;i<100;i++){ // 100 times to improve randomness
	 	j=(rand()%16); // returns [0-15]
	 	swap(j);
	}
	for(i=0;i<N;i++)
		for(j=0;j<N;j++){
			a[i][j]=-1;
			c[i][j]=-1;
			b[i][j]=d[t++];
		}
	a[0][0]=0; // by default 1st cell is selected
	rec();
	setcolor(RED);
	rectangle(90,90,150,150); // red marker for 1st cell
	score(); // print score
}

void play(){
	char m;
	delay(2000); 
	initialise();
	
	do{
		m=getch();
		delay(100);
		check(m);
		if(end==0) // you have completed the game!!
			m='q';
	}while(m!='q');
	
	cleardevice();
	sprintf(str, "%d", point);
	outtextxy(getmaxx()/2, getmaxy()/2, "Congrats! Your Score is: ");
	outtextxy(getmaxx()/2, (getmaxy()/2)+20, str);
	delay(3000);
}


int main()
{	
	int gd=DETECT, gm=VGAMAX;
	initgraph(&gd,&gm,0);
	play();
	closegraph();
	
	return 0;
}
