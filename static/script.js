let currStream;
let currAnalyser;
const bgcolor = getComputedStyle(document.documentElement).getPropertyValue('--bg-color').trim();
const button = document.querySelector(".button_main");

/*
 █████╗ ██╗   ██╗██████╗ ██╗ ██████╗     ██╗   ██╗██╗███████╗██╗   ██╗ █████╗ ██╗     ██╗███████╗███████╗██████╗ 
██╔══██╗██║   ██║██╔══██╗██║██╔═══██╗    ██║   ██║██║██╔════╝██║   ██║██╔══██╗██║     ██║╚══███╔╝██╔════╝██╔══██╗
███████║██║   ██║██║  ██║██║██║   ██║    ██║   ██║██║███████╗██║   ██║███████║██║     ██║  ███╔╝ █████╗  ██████╔╝
██╔══██║██║   ██║██║  ██║██║██║   ██║    ╚██╗ ██╔╝██║╚════██║██║   ██║██╔══██║██║     ██║ ███╔╝  ██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██████╔╝██║╚██████╔╝     ╚████╔╝ ██║███████║╚██████╔╝██║  ██║███████╗██║███████╗███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝       ╚═══╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
*/
const audioCtx = new (AudioContext || webkitAudioContext)();
const songid = document.getElementById('songid');
const stream = document.querySelector("#audioElement");
stream.src = `/static/audio/aud${songid.value}.wav`;
songid.addEventListener("keyup", () => {
	stream.src = `/static/audio/aud${songid.value}.wav`;

});
const playBtn = document.getElementById("play");



stream.addEventListener("ended", () => {
	dataArray2.fill(0);
	dataArray.fill(128);
})

function rollingAverage(dataArray, m) {
	const n = dataArray.length;
	const result = new Float32Array(n);
	for (let i = 0; i < n; i++) {
		let sum = 0;
		for (let j = 0; j < m; j++) {
			const idx = (i + j) % n;
			sum += dataArray[idx];
		}
		result[i] = sum / m;
	}
	return result;
}

function midFreqAvg(dataArray) {
	let sum = 0;
	let count = 0;
	const n = dataArray.length;
	const startIdx = Math.floor(n / 3);
	const endIdx = Math.floor(2 * n / 3);
	for (let i = startIdx; i < endIdx; i++) {
		sum += dataArray[i];
		count++;
	}
	return count ? sum / count : dataArray[startIdx];
}

function fletcherMunsonWeight(frequency) {
	if (frequency < 20) return 0.1;
	if (frequency < 100) return 0.2;
	if (frequency < 500) return 0.5;
	if (frequency < 2000) return 1.0;
	if (frequency < 4000) return 0.8;
	if (frequency < 8000) return 0.6;
	if (frequency < 16000) return 0.4;
	return 0.2;
}


const analyser = audioCtx.createAnalyser();
const sampleRate = audioCtx.sampleRate;
const source = audioCtx.createMediaElementSource(stream);
source.connect(analyser);
source.connect(audioCtx.destination);


playBtn.addEventListener("click", () => {
	if (playBtn.dataset.playing === "false") {
		stream.play();
		playBtn.dataset.playing = "true";
	} else if (playBtn.dataset.playing === "true") {
		stream.pause();
		playBtn.dataset.playing = "false";
	}
})

analyser.fftSize = 256;
const noOfBars = analyser.fftSize / 128;
const bufferLength = analyser.frequencyBinCount;
const minFreq = 20;
const maxFreq = 18000;
const frequencyRange = Math.round(((maxFreq * 2) / sampleRate) * bufferLength + 1);
const logMin = Math.log(minFreq);
const logMax = Math.log(maxFreq);
const logStep = Math.log(maxFreq - minFreq) / (noOfBars - 1);
const logScale = (Math.log(bufferLength)) / (noOfBars - 1);
const logSpread = 1.0001;

const range = frequencyRange;

const dataArray = new Uint8Array(bufferLength).fill(128);
const dataArray2 = new Uint8Array(bufferLength);
let FMArray = new Array(bufferLength).fill(0);
let scaledDataArray2 = new Array(range).fill(0);
const canvas = document.querySelector('#visualizer1');
WIDTH = canvas.width;
HEIGHT = canvas.height;
const canvasCtx = canvas.getContext('2d');
let drawVisual1, drawVisual2, drawVisual3, drawVisual4;
const freqToIdx = (i) => Math.floor(i * (2 * bufferLength / sampleRate));
const idxToFreq = (i) => Math.floor(i * (sampleRate / (2 * bufferLength)));
// const logIdx = (i,n) => Math.floor(Math.exp(logMax - logScale*(n-i)));
const logIdx = (i, n) => (bufferLength - logSpread * Math.exp(logScale * i) + logSpread);

setInterval(() => {
	console.log(dataArray);
	console.log(dataArray2);
	console.log(currStream);
	console.log(currAnalyser);
}, 3000);

function draw() {
	drawVisual1 = requestAnimationFrame(draw);
	//if (!currStream.paused || currStream.active)
	currAnalyser.getByteTimeDomainData(dataArray);
	canvasCtx.fillStyle = "rgb(200 200 200)";
	canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
	canvasCtx.lineWidth = 2;
	canvasCtx.strokeStyle = "rgb(0 0 0)";
	canvasCtx.beginPath();
	const sliceWidth = WIDTH / bufferLength;
	let x = 0;
	for (let i = 0; i < bufferLength; i++) {
		const v = dataArray[i] / 128.0;
		const y = v * (HEIGHT / 2);

		if (i === 0) {
			canvasCtx.moveTo(x, y);
		} else {
			canvasCtx.lineTo(x, y);
		}

		x += sliceWidth;
	}
	canvasCtx.lineTo(WIDTH, HEIGHT / 2);
	canvasCtx.stroke();
}

const canvas2 = document.querySelector('#visualizer2');
WIDTH = canvas2.width;
HEIGHT = canvas2.height;
const canvasCtx2 = canvas2.getContext('2d');

canvas2.addEventListener('click', () => {
	console.log(dataArray2, scaledDataArray2, FMArray);
	console.log(((Date.now()) / 500));

})


// for (let i = 0; i < range; i++) {
// 	const startFreq = Math.floor(Math.exp(logStep*i));
// 	const endtFreq = Math.floor(Math.exp(logStep*(i+1)));

// 	const startIdx = freqToIdx(startFreq);
// 	const endIdx = freqToIdx(endtFreq);
// 	console.log(i, startFreq, endtFreq, startIdx, endIdx);
// }
// console.log(range);
// for(let i=0; i<range; i++){
// 	console.log(logIdx(i,noOfBars))
// }

function draw2() {
	drawVisual2 = requestAnimationFrame(draw2);
	//if (!currStream.paused || currStream.active){
	currAnalyser.getByteFrequencyData(dataArray2);
	FMArray = Array.from(dataArray2, (v, i) => (v + 0.0) * fletcherMunsonWeight(idxToFreq(i)));
	//}
	canvasCtx2.fillStyle = "rgb(200 200 200)";
	canvasCtx2.fillRect(0, 0, WIDTH, HEIGHT);
	canvasCtx2.lineWidth = 2;
	canvasCtx2.strokeStyle = "rgb(0 0 0)";
	canvasCtx2.beginPath();

	const sliceWidth = WIDTH / (range);
	let x = 0;

	for (let i = 0; i < range; i++) {
		// const startFreq = Math.floor(Math.exp(logStep*i));
		// const endtFreq = Math.floor(Math.exp(logStep*(i+1)));

		// const startIdx = freqToIdx(startFreq);
		// const endIdx = freqToIdx(endtFreq);

		// let sum = 0;
		// let count = 0;
		// for (let j = startIdx; j < endIdx && j<bufferLength; j++) {
		// 	sum += dataArray2[j];
		// 	count++;
		// }

		// scaledDataArray2[i] = count ? sum / count : dataArray2[startFreq];
		scaledDataArray2[i] = dataArray2[i];
		scaledDataArray2[i] = scaledDataArray2[i] * Math.log10(i + 7) / Math.log10(range);
		const e = 1.0;
		const gain = 0.5;
		scaledDataArray2[i] = ((scaledDataArray2[i] / 256) ** e) * (2 + gain);


		const y = HEIGHT - (scaledDataArray2[i] * (HEIGHT / 2)) + 1;

		if (i === 0) {
			canvasCtx2.moveTo(x, y);
		} else {
			canvasCtx2.lineTo(x, y);
		}

		x += sliceWidth;
	}
	x = 0;
	canvasCtx2.lineTo(WIDTH, HEIGHT);
	canvasCtx2.stroke();
	canvasCtx2.strokeStyle = 'rgb(255,0,0)';
	canvasCtx2.beginPath();
	for (let i = 0; i < range; i++) {
		const y = HEIGHT - (dataArray2[i] / 128.0 * (HEIGHT / 2)) + 1;

		if (i === 0) {
			canvasCtx2.moveTo(x, y);
		} else {
			canvasCtx2.lineTo(x, y);
		}

		x += sliceWidth;
	}
	canvasCtx2.lineTo(WIDTH, HEIGHT);
	canvasCtx2.stroke();
}




// const canvas3 = document.querySelector('#visualizer3');
// WIDTH3=canvas3.width;
// HEIGHT3=canvas3.height;
// const canvasCtx3 = canvas3.getContext('2d');

// function draw3() {
// 	drawVisual3 = requestAnimationFrame(draw3);
// 	// if(!stream.paused) analyser.getByteFrequencyData(dataArray2);
// 	canvasCtx3.fillStyle = `${bgcolor}`;
// 	canvasCtx3.fillRect(0, 0, WIDTH3, HEIGHT3);


// 	canvasCtx3.shadowBlur = 15;
// 	canvasCtx3.lineWidth = 2;


// 	const now = Date.now();


// 	const r = (v) => {return v*150-1;};
// 	const g =(v) => {return 0};
// 	const b = (v) => {return 255-v*100;};

// 	const shadowGlow=20;

// 	const idleAnimation = (i,minRadius, fr) => {
// 		return minRadius*(1.4+(Math.sin(((i)/fr+(now/5000))*Math.PI*10)))
// 	};

// 	for (let i = 0; i < frequencyRange; i++) {
// 		const v = dataArray2[frequencyRange - i] / 128;
// 		const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i,minRadius,frequencyRange));

// 		canvasCtx3.save();
// 		canvasCtx3.translate(WIDTH3 / 2, HEIGHT3 / 2);
// 		canvasCtx3.rotate((i * Math.PI)/ frequencyRange);

// 		canvasCtx3.beginPath();
// 		canvasCtx3.shadowColor = `rgba(${r(v)+shadowGlow}, ${g(v)+shadowGlow}, ${b(v)+shadowGlow}, 1)`;
// 		canvasCtx3.moveTo(0, innerRadius);
// 		canvasCtx3.lineTo(0, y);
// 		canvasCtx3.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
// 		canvasCtx3.stroke();

// 		canvasCtx3.restore();
// 	}

// 	for (let i = frequencyRange; i < 2*frequencyRange; i++) {
// 		const v = dataArray2[i- frequencyRange] / 128;
// 		const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i,minRadius,frequencyRange));

// 		canvasCtx3.save();
// 		canvasCtx3.translate(WIDTH3 / 2, HEIGHT3 / 2);
// 		canvasCtx3.rotate((i * Math.PI) / frequencyRange);

// 		canvasCtx3.beginPath();
// 		canvasCtx3.shadowColor = `rgba(${r(v)+shadowGlow}, ${g(v)+shadowGlow}, ${b(v)+shadowGlow}, 1)`;
// 		canvasCtx3.moveTo(0, innerRadius);
// 		canvasCtx3.lineTo(0, y);
// 		canvasCtx3.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
// 		canvasCtx3.stroke();

// 		canvasCtx3.restore();
// 	}

// 	canvasCtx3.lineWidth = 3;
// 	canvasCtx3.shadowBlur = 25;
// 	canvasCtx3.strokeStyle = 'rgba(255,255,255, 0.65)';
// 	canvasCtx3.shadowColor = 'rgb(255,255,255)';

// 	const waveRadius = 128;
// 	let averageWave = dataArray;
// 	const waveScale = 5;
// 	const waveOffset = 100;
// 	canvasCtx3.beginPath();

// 	for (let i = 0; i < bufferLength; i++) {
// 		const v = averageWave[i] / 128.0;
// 		const y = v*waveRadius/waveScale + waveOffset;

// 		canvasCtx3.save();
// 		canvasCtx3.translate(WIDTH3 / 2, HEIGHT3 / 2);
// 		canvasCtx3.rotate((i/(bufferLength-1)) *Math.PI*2);

// 		if (i === 0) canvasCtx3.moveTo(0, y);
// 		else canvasCtx3.lineTo(0, y);

// 		canvasCtx3.restore();
// 	}

// 	for (let i = 0; i < bufferLength; i++) {
// 		const v = averageWave[i] / 128.0;
// 		const y = waveRadius*(2-v)/waveScale + waveOffset;
// 		canvasCtx3.save();
// 		canvasCtx3.translate(WIDTH3 / 2, HEIGHT3 / 2);
// 		canvasCtx3.rotate((i/(bufferLength-1)) *Math.PI*2);

// 		if (i === 0) canvasCtx3.moveTo(0, y);
// 		else canvasCtx3.lineTo(0, y);

// 		canvasCtx3.restore();
// 	}
//   	canvasCtx3.stroke();
// }


const canvas4 = document.querySelector('#visualizer4');
const canvasCtx4 = canvas4.getContext('2d');
const
	WIDTH4 = canvas4.width;
HEIGHT4 = canvas4.width;

function draw4() {
	drawVisual4 = requestAnimationFrame(draw4);
	// if(!stream.paused) analyser.getByteFrequencyData(dataArray2);
	canvasCtx4.fillStyle = `${bgcolor}`;
	canvasCtx4.fillRect(0, 0, WIDTH4, HEIGHT4);

	const innerRadius = 70 + 20 * midFreqAvg(scaledDataArray2);
	const minRadius = 2;
	const outerRadius = 25;

	const now = Date.now();


	const r = (v) => { return ((v ** 2) / 1.5) * 200 - 1; };
	const g = (v) => { return 40 };
	const b = (v) => { return 255 - v * 100; };
	const shadowGlow = 20;

	canvasCtx4.shadowBlur = 15;
	canvasCtx4.beginPath();
	canvasCtx4.arc(WIDTH4 / 2, HEIGHT4 / 2, innerRadius, 0, Math.PI * 2);
	canvasCtx4.fillStyle = `rgb(23, 23, 23) `;
	canvasCtx4.fill();
	canvasCtx4.lineWidth = 2;

	button.style.setProperty('--size', 2 * innerRadius + "px");

	const idleAnimation = (i, minRadius, fr) => {
		return minRadius * (3 + (1.5 * Math.sin(((i) / fr + (now / 5000)) * Math.PI * 4)))
	};
	canvasCtx4.save();
	canvasCtx4.translate(WIDTH4 / 2, HEIGHT4 / 2);
	for (let i = 0; i < 2 * range; i++) {
		const v = scaledDataArray2[Math.abs(i - range)];
		const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i, minRadius, range));
		//const angle=(i*2*Math.PI/ (3*range-1)) + (now/5000);
		const angle = (i * Math.PI / (2 * range - 1));

		//canvasCtx4.save();

		//canvasCtx4.rotate((i*2*Math.PI/ (3*range-1)) + (now/5000));

		canvasCtx4.beginPath();
		canvasCtx4.shadowColor = `rgb(${r(v) + shadowGlow}, ${g(v) + shadowGlow}, ${b(v) + shadowGlow})`;
		canvasCtx4.moveTo(-innerRadius * Math.sin(angle), innerRadius * Math.cos(angle));
		canvasCtx4.lineTo(-y * Math.sin(angle), y * Math.cos(angle));
		canvasCtx4.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
		canvasCtx4.stroke();

		//canvasCtx4.restore();
	}
	for (let i = 0; i < 2 * range; i++) {
		const v = scaledDataArray2[Math.abs(i - range)];
		const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i, minRadius, range));
		//const angle=(i*2*Math.PI/ (3*range-1)) + (now/5000);
		const angle = (Math.PI + i * Math.PI / (2 * range - 1));

		//canvasCtx4.save();

		//canvasCtx4.rotate((i*2*Math.PI/ (3*range-1)) + (now/5000));

		canvasCtx4.beginPath();
		canvasCtx4.shadowColor = `rgb(${r(v) + shadowGlow}, ${g(v) + shadowGlow}, ${b(v) + shadowGlow})`;
		canvasCtx4.moveTo(-innerRadius * Math.sin(angle), innerRadius * Math.cos(angle));
		canvasCtx4.lineTo(-y * Math.sin(angle), y * Math.cos(angle));
		canvasCtx4.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
		canvasCtx4.stroke();

		//canvasCtx4.restore();
	}

	canvasCtx4.restore();

	// for (let i = 0; i < range; i++) {
	// 	const v = scaledDataArray2[i];
	// 	const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i,minRadius,range));

	// 	canvasCtx4.save();
	// 	canvasCtx4.translate(WIDTH4 / 2, HEIGHT4 / 2);
	// 	canvasCtx4.rotate(i * 2*Math.PI/ (3*(range-1)) + 2*Math.PI/3);

	// 	canvasCtx4.beginPath();
	// 	canvasCtx4.shadowColor = `rgb(${r(v)+shadowGlow}, ${g(v)+shadowGlow}, ${b(v)+shadowGlow})`;
	// 	canvasCtx4.moveTo(0, innerRadius);
	// 	canvasCtx4.lineTo(0, y);
	// 	canvasCtx4.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
	// 	canvasCtx4.stroke();

	// 	canvasCtx4.restore();
	// }
	// for (let i = 0; i < range; i++) {
	// 	const v = scaledDataArray2[i];
	// 	const y = innerRadius + Math.max(v * outerRadius, idleAnimation(i,minRadius,range));

	// 	canvasCtx4.save();
	// 	canvasCtx4.translate(WIDTH4 / 2, HEIGHT4 / 2);
	// 	canvasCtx4.rotate(i * 2*Math.PI/ (3*(range-1))  + 4*Math.PI/3);

	// 	canvasCtx4.beginPath();
	// 	canvasCtx4.shadowColor = `rgb(${r(v)+shadowGlow}, ${g(v)+shadowGlow}, ${b(v)+shadowGlow})`;
	// 	canvasCtx4.moveTo(0, innerRadius);
	// 	canvasCtx4.lineTo(0, y);
	// 	canvasCtx4.strokeStyle = `rgb(${r(v)}, ${g(v)}, ${b(v)})`;
	// 	canvasCtx4.stroke();

	// 	canvasCtx4.restore();
	// }

	canvasCtx4.lineWidth = 5;
	canvasCtx4.shadowBlur = 50;
	const colour = `rgb(${200 * midFreqAvg(scaledDataArray2)},50,200)`;
	canvasCtx4.strokeStyle = colour;
	canvasCtx4.shadowColor = colour;

	let averageWave = rollingAverage(dataArray, 40);
	const waveRadius = 120 + 1000 * midFreqAvg(scaledDataArray2);
	const waveScale = 40;
	const waveOffset = 140;
	canvasCtx4.beginPath();

	for (let i = 0; i < 4 * bufferLength; i++) {
		const v = averageWave[i % bufferLength] / 128.0;
		const y = v * waveRadius / waveScale + waveOffset;

		canvasCtx4.save();
		canvasCtx4.translate(WIDTH4 / 2, HEIGHT4 / 2);
		//canvasCtx4.rotate((i/(3*bufferLength-1)) *Math.PI*2 + (now/5000));
		canvasCtx4.rotate((i / (4 * bufferLength - 1)) * Math.PI * 2);

		if (i === 0) canvasCtx4.moveTo(0, y);
		else canvasCtx4.lineTo(0, y);

		canvasCtx4.restore();
	}

	for (let i = 0; i < 4 * bufferLength; i++) {
		const v = averageWave[i % bufferLength] / 128.0;
		const y = waveRadius * (2 - v) / waveScale + waveOffset;
		canvasCtx4.save();
		canvasCtx4.translate(WIDTH4 / 2, HEIGHT4 / 2);
		//canvasCtx4.rotate((i/(3*bufferLength-1)) *Math.PI*2 + (now/5000));
		canvasCtx4.rotate((i / (4 * bufferLength - 1)) * Math.PI * 2);

		if (i === 0) canvasCtx4.moveTo(0, y);
		else canvasCtx4.lineTo(0, y);

		canvasCtx4.restore();
	}
	canvasCtx4.stroke();

}



/*
███╗   ███╗██╗ ██████╗██████╗  ██████╗ ██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗███████╗
████╗ ████║██║██╔════╝██╔══██╗██╔═══██╗██╔══██╗██║  ██║██╔═══██╗████╗  ██║██╔════╝
██╔████╔██║██║██║     ██████╔╝██║   ██║██████╔╝███████║██║   ██║██╔██╗ ██║█████╗  
██║╚██╔╝██║██║██║     ██╔══██╗██║   ██║██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║██╔══╝  
██║ ╚═╝ ██║██║╚██████╗██║  ██║╚██████╔╝██║     ██║  ██║╚██████╔╝██║ ╚████║███████╗
╚═╝     ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝
*/

const recordBtn = document.querySelector(".button_main");
let audioChunk = [];
let isRecording = false;
let recorder, recStream;
let audioRecCtx = new (AudioContext || webkitAudioContext)();
let recAnalyser = audioRecCtx.createAnalyser();
let recSource;
let recBlob, recUrl, recAudio;
//console.log(recordBtn.outerHTML);

recAnalyser.fftSize = 256;



recordBtn.addEventListener("click", async () => {
	if (!isRecording) {
		stream.pause();
		recStream = await navigator.mediaDevices.getUserMedia({ audio: true });
		recorder = new MediaRecorder(recStream);


		recSource = audioRecCtx.createMediaStreamSource(recStream);
		recSource.connect(recAnalyser);
		//recSource.connect(audioRecCtx.destination);


		currAnalyser = recAnalyser;
		currStream = recStream;
		//['abort','canplay', 'canplaythrough', 'emptied', 'ended', 'error', 'loadeddata', 'loadedmetadata', 'loadstart', 'pause', 'play', 'playing','progress','suspend','waiting']

		recorder.start();
		recorder.ondataavailable = e => {
			audioChunk = [];
			audioChunk.push(e.data);

		};

		isRecording = true;
		console.log("Recording Starts...");
		console.log(isRecording);

		recorder.onstop = () => {
			console.log("Recording onstop...");
			recBlob = new Blob(audioChunk, { type: 'audio/wav' });
			recUrl = URL.createObjectURL(recBlob);
			recAudio = new Audio(recUrl);


			const formData = new FormData();
			const filename = 'audio_recording.wav';
			formData.append('audio', recBlob, filename);

			fetch('/playground/upload-audio/', {
				method: 'POST',
				body: formData
			})
				.then(res => res.json())
				.then(data => console.log('Success:', data))
				.catch(err => console.error('Upload error:', err));

			// Create a download link and remove this when django backend is working
			const a = document.createElement("a");
			a.href = recUrl;
			a.download = "rec.wav";
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);


			recAudio.addEventListener("start", () => console.log("Recording playing starts"));
			recAudio.addEventListener("ended", () => console.log("Recording playing ended"));
			//recAudio.play();
		}


	} else {
		recorder.stop();
		isRecording = false;
		recStream.getTracks().forEach(track => track.stop());
		//recorder.requestData();
		setTimeout(() => {
			currAnalyser = analyser;
			currStream = stream;
		}, 1000)
		console.log("Recording Stopped");
		console.log(isRecording);
		console.log(recorder.state);
		console.log(audioChunk);
		console.log(recStream.getTracks());
	}
});


window.addEventListener('load', () => {
	if (audioCtx.state === "suspended") {
		audioCtx.resume();
	}
	currAnalyser = analyser;
	currStream = stream;
	draw();
	draw2();
	//draw3();
	draw4();
});

/*
███████╗ ██████╗██████╗ ███████╗███████╗███╗   ██╗    ██████╗ ███████╗ ██████╗ ██████╗ ██████╗ ██████╗ ██╗███╗   ██╗ ██████╗ 
██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝████╗  ██║    ██╔══██╗██╔════╝██╔════╝██╔═══██╗██╔══██╗██╔══██╗██║████╗  ██║██╔════╝ 
███████╗██║     ██████╔╝█████╗  █████╗  ██╔██╗ ██║    ██████╔╝█████╗  ██║     ██║   ██║██████╔╝██║  ██║██║██╔██╗ ██║██║  ███╗
╚════██║██║     ██╔══██╗██╔══╝  ██╔══╝  ██║╚██╗██║    ██╔══██╗██╔══╝  ██║     ██║   ██║██╔══██╗██║  ██║██║██║╚██╗██║██║   ██║
███████║╚██████╗██║  ██║███████╗███████╗██║ ╚████║    ██║  ██║███████╗╚██████╗╚██████╔╝██║  ██║██████╔╝██║██║ ╚████║╚██████╔╝
╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ 
*/


let mediaRecorder;
let recordedChunks = [];

const startBtn = document.getElementById('startBtn');

const startAudioCapture = async () => {
	console.log("START");
	const stream = await navigator.mediaDevices.getDisplayMedia({
		video: true,
		audio: true
	});

	const audioTracks = stream.getAudioTracks();
	const audioOnlyStream = new MediaStream(audioTracks);

	const recorder = new MediaRecorder(audioOnlyStream);
	const chunks = [];

	recSource = audioRecCtx.createMediaStreamSource(stream);
	recSource.connect(recAnalyser);

	currAnalyser = recAnalyser;
	currStream = stream;

	recorder.ondataavailable = (e) => {
		if (e.data.size > 0) chunks.push(e.data);
	};

	recorder.onstop = () => {
		const blob = new Blob(chunks, { type: 'audio/wav' });
		const url = URL.createObjectURL(blob);


		//Send a AJAX POST request to backend at /playground/upload-audio/
		const formData = new FormData();
		const filename = 'audio_recording.wav';
		formData.append('audio', blob, filename);

		fetch('/playground/upload-audio/', {
			method: 'POST',
			body: formData
		})
			.then(res => res.json())
			.then(data => console.log('Success:', data))
			.catch(err => console.error('Upload error:', err));


		// Create a download link and remove this when django backend is working
		// const a = document.createElement('a');
		// a.href = url;
		// a.download = 'audio_recording.wav';
		// a.click();
	};

	recorder.start();

	setTimeout(() => {
		recorder.stop();
		currAnalyser = analyser;
		currStream = stream;
		startBtn.innerHTML = "Record System Audio";
		startBtn.disabled = false;
		startBtn.style.setProperty('--after-display', 'block');
		stream.getTracks().forEach(track => track.stop());
		console.log("STOP");
	}, 15000);

};

startBtn.onclick = async () => {
	startBtn.innerHTML = "Recording...";
	startBtn.disabled = true;
	startBtn.style.setProperty('--after-display', 'none');
	startAudioCapture();
}

